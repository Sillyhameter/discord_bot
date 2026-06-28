// ==UserScript==
// @name         Auto Smelt Debug
// @namespace    http://tampermonkey.net/
// @version      4.0
// @description  Auto smelt with debug logs, matches all common hosts
// @match        *://*.swordmasters.io/*
// @match        *://*.poki.com/*
// @match        *://launch.playcanvas.com/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';
    console.log('[AutoSmeltDebug] Script started!');

    // ===== 配置 =====
    const ENABLED = true;
    const SELECTED_ORES = ['0','1','2','3'];
    // =================

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

    function resetSmeltState() {
        try {
            if (app) {
                if (app.isForgingItem !== undefined) app.isForgingItem = false;
                if (app.loadingPanelController && app.loadingPanelController.enabled !== undefined) app.loadingPanelController.enabled = false;
                if (app.smelterUI && typeof app.smelterUI.close === 'function') app.smelterUI.close();
                if (app.inputEnabled !== undefined) app.inputEnabled = true;
                if (app.networkManager && app.networkManager.room) {
                    app.networkManager.room.send("Client:InventoryController:mergeAll");
                }
            }
        } catch(e) {}
    }

    function doSmelt() {
        if (!ENABLED) return;
        if (!app) { console.log('[AutoSmelt] app not ready'); return; }
        if (!app.networkManager) { console.log('[AutoSmelt] no networkManager'); return; }
        if (!app.networkManager.localInv) { console.log('[AutoSmelt] no localInv'); return; }
        if (!app.networkManager.room) { console.log('[AutoSmelt] no room'); return; }
        if (smeltLock) return;

        const localInv = app.networkManager.localInv;
        const ores = localInv.ores;
        if (!ores || ores.length === 0) {
            console.log('[AutoSmelt] no ores array');
            return;
        }

        console.log('[AutoSmelt] Checking ores, count:', ores.length);

        const countMap = {};
        for (let ore of ores) {
            // 打印第一个矿石的结构，方便调试
            if (Object.keys(countMap).length === 0 && !window._smOreSample) {
                window._smOreSample = ore;
                console.log('[AutoSmelt] Sample ore:', JSON.stringify(ore));
            }
            if (ore.isMelted === true) continue;
            const type = String(ore.type);
            if (SELECTED_ORES.includes(type)) {
                if (!countMap[type]) countMap[type] = { count: 0, itemId: ore.itemId };
                countMap[type].count++;
            }
        }

        console.log('[AutoSmelt] Counts:', JSON.stringify(countMap));

        let targetItemId = null;
        for (let type in countMap) {
            if (countMap[type].count >= 10) {
                targetItemId = countMap[type].itemId;
                break;
            }
        }
        if (!targetItemId) {
            console.log('[AutoSmelt] No ore with >=10 found');
            return;
        }

        console.log('[AutoSmelt] Sending forge for itemId:', targetItemId);
        smeltLock = true;
        app.networkManager.room.send("Client:SmelterController:forge", {
            activeItemId: targetItemId,
            halfChance: true
        });
        showNotification('Auto Smelt: ' + targetItemId + ' x10');

        setTimeout(() => resetSmeltState(), 800);
        setTimeout(() => {
            smeltLock = false;
            resetSmeltState();
        }, 2500);
    }

    function init() {
        console.log('[AutoSmeltDebug] init() called, looking for pc.Application');
        const checkApp = setInterval(() => {
            if (window.pc && window.pc.Application) {
                console.log('[AutoSmeltDebug] pc.Application found');
                const a = window.pc.Application.getApplication();
                if (a) {
                    console.log('[AutoSmeltDebug] app instance obtained');
                    app = a;
                    clearInterval(checkApp);
                    if (interval) clearInterval(interval);
                    interval = setInterval(doSmelt, 800);
                    console.log('[AutoSmeltDebug] interval set, ready');
                    showNotification('Auto Smelt active');
                } else {
                    console.log('[AutoSmeltDebug] getApplication() returned null');
                }
            } else {
                console.log('[AutoSmeltDebug] pc.Application not yet available');
            }
        }, 500);
    }

    // 如果页面已加载，立即执行；否则等加载
    if (document.readyState === 'complete') {
        console.log('[AutoSmeltDebug] document ready complete, calling init');
        init();
    } else {
        console.log('[AutoSmeltDebug] waiting for load event');
        window.addEventListener('load', init);
    }
})();
