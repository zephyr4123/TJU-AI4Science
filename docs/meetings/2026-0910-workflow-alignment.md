# 2026-09-10 架构对齐

- 参与：主人、Claude
- 输入：三个开源仓的代码级深读（[选型 README](../../research/selection/2026-0909-pipeline-frameworks/README.md)）

## 结论

1. 三个仓（InternAgent、autoresearch、AutoResearchClaw）的编排形态相同：外层 for + 硬编码状态判断。差别全在循环之外。"98% 的 workflow 内环都是结果塞 prompt"在编排层成立。
2. 剩余候选（OpenEvolve、AI Scientist v2 等）太旧，不再读。调研阶段结束，转入建骨架。
3. 流程通用，任务不通用。适配是写文件不是改代码：任务包 + 领域包，扫目录发现。
4. 三箱结构：框架（决策与校验）、底座（唯一执行者）、工具（确定性脚本）。
5. 底座 coding agent 是唯一执行者，写代码、写文档、文献检索都归它；一个阶段一次新会话，上下文从磁盘来；框架零模型调用。
6. 裁判是上下文隔离的 agent：确定性能判的用 runner 与零 LLM 判据；需要模型判断的派新会话（可不同模型），只给产物不给轨迹。
7. 不设专门的"反思" agent；反思换成确定性检查再喂回底座。
8. 文档体系：`docs/architecture/` 是可改的总纲领（改要双方认可 + 变更记录），`docs/specs/` 每版一份 PRD，`docs/adr/` 只留仓库基础设施的决定，`docs/meetings/` 记结论。
9. 协作规范：spec coding + issue driven。先对齐 spec 再干活，文档实时更新，每个工作单元一条 issue，过程即结果。

## 待办

- [x] 写 `architecture/` 四份、`specs/v0.1-demo.md`、本纪要
- [ ] 主人审 `specs/v0.1-demo.md`，转 aligned
- [x] 目标合约 [#2](https://github.com/zephyr4123/TJU-AI4Science/issues/2)；五条母 issue [#3](https://github.com/zephyr4123/TJU-AI4Science/issues/3) 到 [#7](https://github.com/zephyr4123/TJU-AI4Science/issues/7) 挂 milestone v0.1；叶子开工时再拆 sub-issue
- [x] Q-1 到 Q-9 各一条 [#8](https://github.com/zephyr4123/TJU-AI4Science/issues/8) 到 [#16](https://github.com/zephyr4123/TJU-AI4Science/issues/16)，`needs-decision`
- [x] 科研案例采集 [#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1)，挂在 #4 下
- [ ] 内仓远端地址
