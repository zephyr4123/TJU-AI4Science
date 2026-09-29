// 公众号稿（#193）的界面截图：真服务、真数据、2 倍清晰度、浅色。
//
// 数据根只放 GUA 一个项目（首页干净）：
//   cp -Rpc materials/home/projects/gua  <根>/projects/
//   cp -Rpc materials/home/studio        <根>/
//   cd platform && AI4SCI_HOME=<根> .venv/bin/ai4sci serve --port 8766
// 然后在 playwright MCP 里跑 browser_run_code_unsafe，filename 指向本文件。
// 相对路径按 MCP 的工作目录（外层仓根）解析。
async (page) => {
  const BASE = 'http://127.0.0.1:8766/';
  const OUT = 'materials/articles/2026-0929-first-release/figures/';   // 出图落本机（gitignore），upload.py 传 COS
  const ctx = await page.context().browser().newContext({
    deviceScaleFactor: 2, viewport: { width: 1440, height: 900 }, colorScheme: 'light',
  });
  const p = await ctx.newPage();
  const settle = (ms = 1200) => p.waitForTimeout(ms);
  const shots = [];
  const shot = async (name, opts = {}) => { await p.screenshot({ path: OUT + name, ...opts }); shots.push(name); };
  const collapseChat = async () => {
    const btn = p.getByRole('button', { name: /收起对话|Close/ }).first();
    if (await btn.isVisible().catch(() => false)) { await btn.click(); await settle(600); }
  };

  // 首页：项目墙
  await p.goto(BASE); await settle(2500);
  await shot('ui-home.png', { clip: { x: 0, y: 0, width: 1440, height: 560 } });

  // 项目页：居中的对话入口 + 工作区清单
  await p.getByText('复现 GUA').first().click(); await settle();
  await shot('ui-project.png');

  // 工作区：看板（论文复现这条流程走到哪、每格几次产出）
  await p.setViewportSize({ width: 1600, height: 900 });
  await p.getByRole('button', { name: /^完成 复现 GUA/ }).click(); await settle(1500);
  await collapseChat();
  await shot('ui-workspace-board.png', { clip: { x: 0, y: 0, width: 1600, height: 620 } });

  // 演练的原始对话：开头、结果并排、收尾
  await p.setViewportSize({ width: 1440, height: 1060 });   // 对话区约 750 px 高：手机上一张不超过大半屏
  await p.getByRole('button', { name: /打开对话/ }).first().click(); await settle();
  await p.getByRole('button', { name: '打开对话列表' }).click(); await settle(600);
  await p.getByRole('button', { name: /^我有一篇论文/ }).click(); await settle(2000);
  const body = p.locator('div.relative.min-h-0.flex-1.overflow-y-auto').first();
  const at = async (marker, name) => {
    if (marker) {
      await p.getByText(marker, { exact: false }).first().evaluate((el) => el.scrollIntoView({ block: 'start' }));
      await body.evaluate((el) => { el.scrollTop -= 16; });
    } else {
      await body.evaluate((el) => { el.scrollTop = 0; });
    }
    await settle(800);
    await body.screenshot({ path: OUT + name }); shots.push(name);
  };
  await at(null, 'ui-chat-open.png');
  await at('跑完了，两行数都落在需求定的标准里', 'ui-chat-result.png');
  await at('到验收了', 'ui-chat-rewrite.png');       // 第一版分析过了核对、通读发现笔误，重写与被拦
  await at('给老师的一句话结论', 'ui-chat-end.png');

  // 编辑台：流程库、两条出厂流程、能力库
  await p.setViewportSize({ width: 1440, height: 900 });
  await p.getByRole('button', { name: '编辑台' }).click(); await settle();
  await collapseChat();
  await p.getByText('流程库', { exact: true }).click(); await settle(600);
  await shot('ui-studio-library.png', { clip: { x: 0, y: 0, width: 1440, height: 420 } });
  await p.getByRole('button', { name: '论文复现 6 项，出厂' }).click(); await settle(1500);
  await shot('ui-studio-reproduce.png', { clip: { x: 72, y: 56, width: 1368, height: 580 } });
  await p.getByText('流程库', { exact: true }).click(); await settle(600);
  await p.getByRole('button', { name: /^从设计到验证/ }).click(); await settle(1500);
  await shot('ui-studio-research.png', { clip: { x: 72, y: 56, width: 1368, height: 580 } });
  await p.getByText('能力', { exact: true }).first().click(); await settle(1500);
  await shot('ui-studio-caps.png', { clip: { x: 0, y: 0, width: 1440, height: 470 } });

  // 设置：只截 AI 那一栏（两家 agent 与自检状态）；算力那一栏有主机地址，不截
  await p.getByRole('button', { name: /^设置/ }).click(); await settle(1500);
  await shot('ui-settings-agents.png', { clip: { x: 84, y: 12, width: 800, height: 450 } });

  await ctx.close();
  return shots;
}
