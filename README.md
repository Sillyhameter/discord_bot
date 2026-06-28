const iframe = document.querySelector('iframe');
if (iframe) {
    const win = iframe.contentWindow;
    // 清除之前的脚本
    win.document.querySelectorAll('script').forEach(s => {
        if (s.textContent.includes('auto-smelt')) s.remove();
    });
    const script = win.document.createElement('script');
    script.textContent = `
        // == auto-smelt 增强版 ==
        (function() {
            console.log('[AutoSmelt] 增强版已启动');

            // 矿石名称映射
            const ORE_MAP = {'0':'Coal','1':'Emerald','2':'Diamond','3':'Ruby'};
            const SELECTED = ['0','1','2','3']; // 要熔炼的矿石类型

            function getOreCounts() {
                // 尝试从游戏数据获取矿石数量
                try {
                    // 方法1: 通过 window.app (如果存在)
                    if (window.app && window.app.networkManager && window.app.networkManager.localInv) {
                        const ores = window.app.networkManager.localInv.ores;
                        if (ores) {
                            const counts = {};
                            for (let ore of ores) {
                                if (ore.isMelted) continue;
                                const type = String(ore.type);
                                if (SELECTED.includes(type)) {
                                    counts[type] = (counts[type] || 0) + 1;
                                }
                            }
                            return counts;
                        }
                    }
                } catch(e) {}

                // 方法2: 从 UI 读取显示的数量
                try {
                    const oreElements = document.querySelectorAll('[data-ore-count], .ore-count, .ore-amount');
                    for (let el of oreElements) {
                        const text = el.textContent || '';
                        const match = text.match(/(\\d+)/);
                        if (match) {
                            const count = parseInt(match[1], 10);
                            const parent = el.closest('[data-ore-type]') || el.parentElement;
                            const type = parent ? parent.getAttribute('data-ore-type') : '';
                            if (type && SELECTED.includes(type)) {
                                return {[type]: count};
                            }
                        }
                    }
                } catch(e) {}

                return null;
            }

            function findSmeltButton() {
                const btns = document.querySelectorAll('button, div[role="button"], span[role="button"], .btn, [class*="smelt"], [class*="forge"]');
                for (let btn of btns) {
                    const text = (btn.innerText || btn.textContent || '').toLowerCase();
                    if (text.includes('smelt') || text.includes('熔炼') || text.includes('forge')) {
                        if (btn.offsetParent !== null && !btn.disabled) {
                            return btn;
                        }
                    }
                }
                return null;
            }

            let lastClickTime = 0;
            setInterval(() => {
                const btn = findSmeltButton();
                if (!btn) {
                    console.log('[AutoSmelt] 未找到熔炼按钮');
                    return;
                }

                // 检查矿石数量（如果有）
                const counts = getOreCounts();
                if (counts) {
                    let total = 0;
                    for (let type in counts) {
                        total += counts[type];
                    }
                    if (total < 10) {
                        // 如果总数少于10，不点击
                        console.log('[AutoSmelt] 矿石不足10个 (当前:', total, ')');
                        return;
                    }
                    console.log('[AutoSmelt] 矿石数量:', counts);
                } else {
                    // 如果读不到数量，保守点击（每5秒最多一次）
                    if (Date.now() - lastClickTime < 5000) {
                        return;
                    }
                }

                // 点击熔炼
                btn.click();
                lastClickTime = Date.now();
                console.log('[AutoSmelt] ✅ 点击熔炼');
            }, 1500);
        })();
    `;
    win.document.head.appendChild(script);
    console.log('✅ 增强版脚本已注入');
} else {
    console.log('❌ 未找到 iframe');
}
