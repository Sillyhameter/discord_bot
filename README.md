// 生成一个永久有效的 Sword Masters Pro 卡密
(async function generateLicense() {
    // 1. 从脚本中提取的硬编码 secret（与朋友脚本相同）
    const secretArray = [
        -0x3 * -0x822 + -0xf4c + 0x1 * -0x8f9,
        -0x9 * 0x103 + -0x1 * 0x11a5 + 0x1af6,
        0x1e7 + 0xf3 + 0xaa * -0x4,
        0x3d1 * 0x7 + -0x110a + -0x97d,
        0xb8 * 0x1e + 0x1e58 + -0x19db * 0x2,
        -0x1 * 0x17f8 + -0x1238 * -0x1 + 0x61f * 0x1,
        0x1eae + 0x423 * 0x6 + 0xd * -0x43c,
        0x4cd * -0x5 + -0x2b1 * 0xd + -0x17 * -0x295,
        -0x81d * 0x1 + 0x517 * 0x7 + -0x1b12,
        0xa4 + -0x1935 + 0x18f4,
        0x12d6 + 0x1b1b + -0x2d8c,
        0x20f2 * -0x1 + 0x779 + -0xce6 * -0x2,
        -0x60a + -0x17e9 + -0x1 * -0x1e52,
        -0x395 * -0x1 + 0x1100 + -0x1 * 0x1426,
        -0x11cc + 0xdcd * 0x1 + 0x471,
        0xe36 + 0x1b08 + -0x1 * 0x28d9,
        0x2385 * 0x1 + 0x15df * -0x1 + -0xd56,
        0x2272 + -0xd * -0xfe + -0x2ee5,
        0x1282 * 0x1 + -0x12 * 0x54 + 0xc28 * -0x1,
        0x5f4 * 0x1 + -0xcc2 * -0x3 + -0x2bd5,
        0xc94 + 0x43b + -0x105b,
        -0xeee + 0x14ae + -0x3b * 0x17,
        0x1 * -0x18b3 + 0x11 * -0x115 + -0x1 * -0x2b79,
        0x3a9 * -0xa + -0x1176 + 0x365d,
        0x1e15 + 0x23 * 0x8b + -0x30b2,
        0x1131 + 0x2 * 0x110d + 0x32d9 * -0x1,
        0x21da + -0x1 * -0x1473 + -0x35de,
        0x609 + 0x1 * 0x20b6 + -0x8 * 0x4cd
    ];
    // 将数组反转并转为字符串（逆序操作）
    const secret = secretArray.slice().reverse().map(x => String.fromCharCode(x)).join('');

    // 2. 设置日期（永不过期：2099-12-31）
    const year = 2099, month = 12, day = 31;
    const dateStr = `${year}${String(month).padStart(2, '0')}${String(day).padStart(2, '0')}`;

    // 3. 计算 HMAC-SHA256 签名
    const encoder = new TextEncoder();
    const keyData = encoder.encode(secret);
    const message = encoder.encode(dateStr);

    try {
        const cryptoKey = await crypto.subtle.importKey(
            'raw', keyData,
            { name: 'HMAC', hash: 'SHA-256' },
            false, ['sign']
        );
        const signature = await crypto.subtle.sign('HMAC', cryptoKey, message);
        const hashArray = Array.from(new Uint8Array(signature));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        const sig = hashHex.slice(0, 16); // 取前16位

        const license = `SM-${dateStr}-${sig}`;
        console.log('✅ 新卡密生成成功:');
        console.log(license);
        console.log('复制上面这串卡密，即可使用。');
        // 自动复制到剪贴板（如果浏览器允许）
        try {
            await navigator.clipboard.writeText(license);
            console.log('已自动复制到剪贴板！');
        } catch(e) {}
    } catch (err) {
        console.error('生成失败:', err);
        // 备用方案：如果 crypto.subtle 不可用，输出一个占位卡密（但签名无效，需配合验证绕过）
        console.warn('使用备用卡密（需配合绕过验证）: SM-20991231-aaaaaaaaaaaaaaaa');
    }
})();
