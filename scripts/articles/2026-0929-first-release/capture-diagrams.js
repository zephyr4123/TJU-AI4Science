// 公众号稿（#193）的示意图出图：diagrams.html 里每个 .fig 截一张，3 倍清晰度（720 → 2160 px）。
// 先跑 diagrams.py 生成 materials/articles/2026-0929-first-release/diagrams.html，再在那个目录起
//   python3 -m http.server 8770 --bind 127.0.0.1
// 用 localhost 访问（CDN 的 referer 白名单认它）。然后在 playwright MCP 里跑 browser_run_code_unsafe，filename 指向本文件。
async (page) => {
  const OUT = 'materials/articles/2026-0929-first-release/figures/';   // 出图落本机（gitignore），upload.py 传 COS
  const ctx = await page.context().browser().newContext({
    deviceScaleFactor: 3, viewport: { width: 820, height: 1200 }, colorScheme: 'light',
  });
  const p = await ctx.newPage();
  await p.goto('http://localhost:8770/diagrams.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const ids = await p.$$eval('section.fig', (els) => els.map((e) => e.id));
  for (const id of ids) {
    await p.locator('#' + id).screenshot({ path: OUT + id + '.png' });
  }
  await ctx.close();
  return ids;
}
