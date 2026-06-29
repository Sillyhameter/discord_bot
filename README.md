// ==UserScript==
// @name         Auto Smelt Panel (F8)
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  Auto smelt ores with UI, F8 toggle, no license
// @match        *://*.swordmasters.io/*
// @match        *://*.poki.com/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // ===== 配置 =====
    const ORE_TYPES = {
        '0': 'Coal',
        '1': 'Emerald',
        '2': 'Diamond',
        '3': 'Ruby'
    };
    const STORAGE_KEY = 'sm_auto_smelt_panel_config';
    // =================

    let app = null;
    let smeltLock = false;
    let interval = null;
    let panelVisible = false;

    // 读取/保存配置
    function loadConfig() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {
                const cfg = JSON.parse(raw);
                return cfg;
            }
        } catch(e) {}
        return { enabled: true, selectedOres: ['0','1','2','3'] };
    }

    function saveConfig(cfg) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(cfg));
    }

    let config = loadConfig();

    // ===== UI 创建 =====
    function createUI() {
        // 注入样式
        const style = document.createElement('style');
        style.textContent = `
            #sm-panel {
                position: fixed;
                top: 100px;
                right: 20px;
                width: 220px;
                background: rgba(20, 20, 25, 0.92);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 16px 18px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.6);
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                color: #f0f0f0;
                z-index: 999999;
                display: none;
                user-select: none;
                transition: opacity 0.2s;
                min-width: 180px;
            }
            #sm-panel .sm-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
                font-weight: 600;
                font-size: 15px;
                letter-spacing: 0.3px;
            }
            #sm-panel .sm-header .sm-title {
                display: flex;
                align-items: center;
                gap: 6px;
            }
            #sm-panel .sm-header .sm-title svg {
                width: 18px;
                height: 18px;
                fill: none;
                stroke: currentColor;
                stroke-width: 2;
                stroke-linecap: round;
                stroke-linejoin: round;
            }
            #sm-panel .sm-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 6px 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            #sm-panel .sm-row:last-child {
                border-bottom: none;
            }
            #sm-panel .sm-label {
                font-size: 13px;
                color: #ccc;
            }
            /* Toggle Switch */
            .sm-toggle {
                position: relative;
                display: inline-block;
                width: 40px;
                height: 22px;
                flex-shrink: 0;
                cursor: pointer;
            }
            .sm-toggle input {
                opacity: 0;
                width: 0;
                height: 0;
            }
            .sm-toggle .slider {
                position: absolute;
                inset: 0;
                background-color: #555;
                border-radius: 34px;
                transition: 0.3s;
            }
            .sm-toggle .slider::before {
                content: '';
                position: absolute;
                height: 16px;
                width: 16px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                border-radius: 50%;
                transition: 0.3s;
            }
            .sm-toggle input:checked + .slider {
                background-color: #6366f1;
            }
            .sm-toggle input:checked + .slider::before {
                transform: translateX(18px);
            }

            .sm-gear {
                cursor: pointer;
                opacity: 0.6;
                transition: 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 24px;
                height: 24px;
                border-radius: 50%;
            }
            .sm-gear:hover {
                opacity: 1;
                background: rgba(255,255,255,0.1);
            }
            .sm-gear svg {
                width: 18px;
                height: 18px;
                fill: none;
                stroke: currentColor;
                stroke-width: 2;
                stroke-linecap: round;
                stroke-linejoin: round;
            }

            .sm-settings {
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid rgba(255,255,255,0.08);
                display: none;
                flex-direction: column;
                gap: 6px;
            }
            .sm-settings.open {
                display: flex;
            }
            .sm-settings .sm-ore-item {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 13px;
                color: #ddd;
                cursor: pointer;
                padding: 4px 6px;
                border-radius: 4px;
                transition: background 0.2s;
            }
            .sm-settings .sm-ore-item:hover {
                background: rgba(255,255,255,0.05);
            }
            .sm-settings .sm-ore-item input[type="checkbox"] {
                width: 16px;
                height: 16px;
                accent-color: #6366f1;
                cursor: pointer;
            }
            .sm-settings .sm-ore-item label {
                cursor: pointer;
                flex: 1;
            }
            .sm-status {
                font-size: 11px;
                color: #999;
                margin-top: 8px;
                text-align: right;
                border-top: 1px solid rgba(255,255,255,0.05);
                padding-top: 6px;
            }
        `;
        document.head.appendChild(style);

        // 面板 HTML
        const panel = document.createElement('div');
        panel.id = 'sm-panel';
        panel.innerHTML = `
            <div class="sm-header">
                <span class="sm-title">
                    <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                    Auto Smelt
                </span>
                <div class="sm-gear" id="sm-gear-btn">
                    <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                </div>
            </div>
            <div class="sm-row">
                <span class="sm-label">Enable</span>
                <label class="sm-toggle">
                    <input type="checkbox" id="sm-enable-toggle" ${config.enabled ? 'checked' : ''}>
                    <span class="slider"></span>
                </label>
            </div>
            <div class="sm-settings" id="sm-settings-area">
                ${Object.entries(ORE_TYPES).map(([key, label]) => `
                    <div class="sm-ore-item">
                        <input type="checkbox" id="ore-${key}" value="${key}" ${config.selectedOres.includes(key) ? 'checked' : ''}>
                        <label for="ore-${key}">${label}</label>
                    </div>
                `).join('')}
            </div>
            <div class="sm-status" id="sm-status">${config.enabled ? 'Active' : 'Disabled'}</div>
        `;

        document.body.appendChild(panel);

        // ---- 事件绑定 ----
        // 开关
        const toggle = document.getElementById('sm-enable-toggle');
        toggle.addEventListener('change', function() {
            config.enabled = this.checked;
            saveConfig(config);
            document.getElementById('sm-status').textContent = config.enabled ? 'Active' : 'Disabled';
            if (!config.enabled) {
                // 停止熔炼（但循环还在，只是跳过）
            }
        });

        // 齿轮切换设置
        const gearBtn = document.getElementById('sm-gear-btn');
        const settingsArea = document.getElementById('sm-settings-area');
        gearBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            settingsArea.classList.toggle('open');
        });

        // 矿石复选框
        document.querySelectorAll('#sm-settings-area input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', function() {
                const checked = document.querySelectorAll('#sm-settings-area input[type="checkbox"]:checked');
                config.selectedOres = Array.from(checked).map(c => c.value);
                saveConfig(config);
            });
        });

        // 点击面板外部不关闭（但可以点击齿轮关闭设置）
        // 按F8切换显示
        window.addEventListener('keydown', function(e) {
            if (e.key === 'F8' || e.code === 'F8') {
                e.preventDefault();
                panelVisible = !panelVisible;
                panel.style.display = panelVisible ? 'block' : 'none';
            }
        });

        // 初始隐藏
        panel.style.display = 'none';

        // 如果点击齿轮，不冒泡
        settingsArea.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    // ===== 熔炼核心逻辑 =====
    function resetSmeltUI() {
        try {
            if (!app) return;
            if (app.isForgingItem !== undefined) app.isForgingItem = false;
            if (app.isSmelterEnabled !== undefined) app.isSmelterEnabled = false;
            const root = app.root;
            if (root && typeof root.findComponents === 'function') {
                const panels = root.findComponents('itemForgedPanelBlackBackground');
                if (panels) {
                    for (let p of panels) {
                        if (p.enabled !== undefined) p.enabled = false;
                        if (p.element) p.element.opacity = 0;
                    }
                }
                const smelters = root.findComponents('smelterController');
                if (smelters) {
                    for (let s of smelters) {
                        if (s.isForging !== undefined) s.isForging = false;
                        if (s.isSmelterEnabled !== undefined) s.isSmelterEnabled = false;
                    }
                }
            }
            if (app.networkManager && app.networkManager.room) {
                app.networkManager.room.send("Client:InventoryController:mergeAll");
            }
        } catch(e) {}
    }

    function doSmelt() {
        if (!config.enabled) return;
        if (!app || !app.networkManager || !app.networkManager.localInv || !app.networkManager.room) return;
        if (smeltLock) return;

        const localInv = app.networkManager.localInv;
        const ores = localInv.ores;
        if (!ores || ores.length === 0) return;

        const selected = config.selectedOres;
        if (selected.length === 0) return;

        const countMap = {};
        for (let ore of ores) {
            if (ore.isMelted === true) continue;
            const type = String(ore.type);
            if (selected.includes(type)) {
                if (!countMap[type]) countMap[type] = { count: 0, itemId: ore.itemId };
                countMap[type].count++;
            }
        }

        let targetItemId = null;
        for (let type in countMap) {
            if (countMap[type].count >= 10) {
                targetItemId = countMap[type].itemId;
                break;
            }
        }
        if (!targetItemId) return;

        smeltLock = true;
        app.networkManager.room.send("Client:SmelterController:forge", {
            activeItemId: targetItemId,
            halfChance: true
        });

        setTimeout(() => {
            resetSmeltUI();
            setTimeout(() => resetSmeltUI(), 500);
        }, 800);

        setTimeout(() => {
            smeltLock = false;
        }, 2500);
    }

    // ===== 初始化 =====
    function init() {
        // 创建UI
        createUI();

        // 等待游戏加载
        const checkApp = setInterval(() => {
            if (window.pc && window.pc.Application) {
                const a = window.pc.Application.getApplication();
                if (a) {
                    app = a;
                    clearInterval(checkApp);
                    if (interval) clearInterval(interval);
                    interval = setInterval(doSmelt, 800);
                    console.log('[AutoSmelt Panel] 已注入游戏');
                }
            }
        }, 500);
    }

    if (document.readyState === 'complete') init();
    else window.addEventListener('load', init);
})();
