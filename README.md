// ==UserScript==
// @name         Auto Smelt (Fixed + Reset)
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  Auto smelt ores when >=10, with UI reset to prevent freeze
// @match        *://*.swordmasters.io/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';
    let app = null;
    let smeltLock = false;
    let interval = null;

    function getConfig() {
        try {
            const raw = localStorage.getItem('sm_pro_config');
            if (raw) return JSON.parse(raw);
        } catch(e) {}
        return {};
    }

    function showNotification(msg) {
        const area = document.getElementById('sm-notifs');
        if (area) {
            const div = document.createElement('div');
            div.className = 'sm-notification';
            div.textContent = msg;
            area.appendChild(div);
            setTimeout(() => { div.style.opacity = '0'; div.style.transform = 'translateY(20px)'; setTimeout(() => div.remove(), 300); }, 3000);
        } else {
            console.log('[AutoSmelt]', msg);
        }
    }

    // 强制重置熔炼相关的锁定和UI
    function resetSmeltState() {
        try {
            // 1. 重置游戏内的熔炼标志
            if (app.isForgingItem !== undefined) {
                app.isForgingItem = false;
            }
            // 2. 关闭加载遮罩（如果有）
            if (app.loadingPanelController && app.loadingPanelController.enabled !== undefined) {
                app.loadingPanelController.enabled = false;
            }
            // 3. 如果有熔炼界面控制器，尝试关闭
            if (app.smelterUI && typeof app.smelterUI.close === 'function') {
                app.smelterUI.close();
            }
            // 4. 如果有全局的UI锁定，解除（有些游戏用 inputEnabled）
            if (app.inputEnabled !== undefined) {
                app.inputEnabled = true;
            }
            // 5. 触发库存刷新（发送一个无害的请求，如合并，迫使同步）
            if (app.networkManager && app.networkManager.room) {
                // 发送一个空操作或合并请求，让服务器响应以唤醒客户端
                app.networkManager.room.send("Client:InventoryController:mergeAll");
            }
        } catch(e) {
            // 忽略错误
        }
    }

    function doSmelt() {
        const config = getConfig();
        if (!config.autoSmeltEnabled) return;
        if (!app || !app.networkManager || !app.networkManager.localInv || !app.networkManager.room) return;
        if (app.isForgingItem || smeltLock) return;

        const localInv = app.networkManager.localInv;
        const ores = localInv.ores;
        if (!ores || ores.length === 0) return;

        const selectedTypes = (config.autoSmeltSelectedOres || ['0','1','2','3']).map(String);
        const countMap = {};

        for (let ore of ores) {
            if (ore.isMelted) continue;
            const type = String(ore.type);
            if (selectedTypes.includes(type)) {
                if (!countMap[type]) countMap[type] = { count: 0, itemId: ore.itemId };
                countMap[type].count++;
            }
        }

        let foundItemId = null;
        for (let type in countMap) {
            if (countMap[type].count >= 10) {
                foundItemId = countMap[type].itemId;
                break;
            }
        }
        if (!foundItemId) return;

        // 锁定，避免重复
        smeltLock = true;

        // 发送熔炼请求
        app.networkManager.room.send("Client:SmelterController:forge", {
            activeItemId: foundItemId,
            halfChance: true
        });

        showNotification(`Auto Smelt: ${foundItemId} x10`);

        // 延迟重置状态（等待动画时间，约2秒）
        setTimeout(() => {
            resetSmeltState();
            smeltLock = false;
        }, 2000);

        // 额外保险：如果3秒后仍未解锁，强制解锁
        setTimeout(() => {
            if (smeltLock) {
                resetSmeltState();
                smeltLock = false;
                showNotification("Smelt reset (forced)");
            }
        }, 3500);
    }

    function init() {
        const checkApp = setInterval(() => {
            if (window.pc && window.pc.Application) {
                const a = window.pc.Application.getApplication();
                if (a) {
                    app = a;
                    clearInterval(checkApp);
                    if (interval) clearInterval(interval);
                    interval = setInterval(doSmelt, 600);
                    console.log('[AutoSmelt] Fixed version loaded.');
                    showNotification("Auto Smelt (fixed) active");
                }
            }
        }, 200);
    }

    if (document.readyState === 'complete') init();
    else window.addEventListener('load', init);
})();
