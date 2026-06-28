// ==UserScript==
// @name         Auto Smelt (Standalone Fix)
// @namespace    http://tampermonkey.net/
// @version      3.0
// @description  Auto smelt ores when >=10, no UI freeze, independent config
// @match        *://*.swordmasters.io/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // ========== 用户配置（直接改这里） ==========
    const ENABLED = true;                     // true=启用，false=禁用
    const SELECTED_ORES = ['0', '1', '2', '3']; // 0=Coal, 1=Emerald, 2=Diamond, 3=Ruby
    const SMELT_INTERVAL = 800;               // 检查间隔（毫秒）
    const LOCK_DURATION = 2500;               // 熔炼后锁定时间（毫秒）
    // ===========================================

    let app = null;
    let smeltLock = false;
    let interval = null;

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

    // 强制重置熔炼状态（防止卡死）
    function resetSmeltState() {
        try {
            if (app) {
                if (app.isForgingItem !== undefined) app.isForgingItem = false;
                if (app.loadingPanelController && app.loadingPanelController.enabled !== undefined) app.loadingPanelController.enabled = false;
                if (app.smelterUI && typeof app.smelterUI.close === 'function') app.smelterUI.close();
                if (app.inputEnabled !== undefined) app.inputEnabled = true;
                // 发送一个无害的同步请求
                if (app.networkManager && app.networkManager.room) {
                    app.networkManager.room.send("Client:InventoryController:mergeAll");
                }
            }
        } catch(e) {}
    }

    function doSmelt() {
        if (!ENABLED) return;
        if (!app || !app.networkManager || !app.networkManager.localInv || !app.networkManager.room) return;
        if (smeltLock) return;

        const localInv = app.networkManager.localInv;
        const ores = localInv.ores;
        if (!ores || ores.length === 0) return;

        // 统计未熔炼的矿石数量
        const countMap = {};
        for (let ore of ores) {
            // 有些矿石有 isMelted 属性，有些没有，没有则视为未熔炼
            if (ore.isMelted === true) continue;
            const type = String(ore.type);
            if (SELECTED_ORES.includes(type)) {
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

        // 锁定，避免重复
        smeltLock = true;

        // 发送熔炼请求（有些服务器需要 count，有些只需要 itemId）
        app.networkManager.room.send("Client:SmelterController:forge", {
            activeItemId: targetItemId,
            halfChance: true   // 如果服务器不接受，可以改为 count: 10
        });

        showNotification(`Auto Smelt: ${targetItemId} x10`);

        // 熔炼后立即复位（但保留一点延迟让动画触发）
        setTimeout(() => {
            resetSmeltState();
        }, 800);

        // 解锁
        setTimeout(() => {
            smeltLock = false;
            // 再次复位，确保界面恢复
            resetSmeltState();
        }, LOCK_DURATION);
    }

    function init() {
        const checkApp = setInterval(() => {
            if (window.pc && window.pc.Application) {
                const a = window.pc.Application.getApplication();
                if (a) {
                    app = a;
                    clearInterval(checkApp);
                    if (interval) clearInterval(interval);
                    interval = setInterval(doSmelt, SMELT_INTERVAL);
                    console.log('[AutoSmelt] Standalone fix loaded.');
                    showNotification('Auto Smelt (standalone) active');
                }
            }
        }, 200);
    }

    if (document.readyState === 'complete') init();
    else window.addEventListener('load', init);
})();
