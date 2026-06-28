// ==UserScript==
// @name         Auto Smelt (Fixed Window)
// @namespace    http://tampermonkey.net/
// @version      10.0
// @description  Auto clicks smelt at fixed pixel position
// @match        *://*.swordmasters.io/*
// @match        *://*.poki.com/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';
    // === 在这里填入你捕获的坐标 ===
    const CLICK_X = 176;   // 替换成你的 X
    const CLICK_Y = 354;   // 替换成你的 Y
    // ================================

    console.log('[AutoSmelt] 固定窗口模式启动，坐标:', CLICK_X, CLICK_Y);

    setInterval(() => {
        const iframe = document.querySelector('iframe');
        if (!iframe) return;
        const rect = iframe.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;

        const targetX = rect.left + CLICK_X;
        const targetY = rect.top + CLICK_Y;

        // 模拟鼠标点击
        const event = new MouseEvent('click', {
            view: window,
            bubbles: true,
            cancelable: true,
            clientX: targetX,
            clientY: targetY
        });
        document.dispatchEvent(event);

        // 也尝试在 iframe 内部分发
        try {
            const win = iframe.contentWindow;
            if (win) {
                const event2 = new MouseEvent('click', {
                    view: win,
                    bubbles: true,
                    cancelable: true,
                    clientX: rect.left + CLICK_X,
                    clientY: rect.top + CLICK_Y
                });
                win.document.dispatchEvent(event2);
            }
        } catch(e) {}

        console.log('[AutoSmelt] 点击熔炼');
    }, 2000);
})();
