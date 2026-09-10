# 2026-09-10 协调层对齐

- 参与：主人、Claude
- 输入：[上午的架构对齐](2026-0910-workflow-alignment.md)；主人提出"各家 coding agent CLI 只是链路中间的执行一环，整条链路是谁在决策和组织"
- 落地：[#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)

## 结论

1. 旧纲领把"机械判定"和"科研判断"揉在框架里。后者没有家，被塞进"设计阶段一次会话"和"人在环文件通道"；固定顺序的阶段骨架本质就是三个开源仓的"外层 for + 硬编码状态"，只是写在流程图里。
2. 加协调层 = 人（PI）+ 协调 agent（科研助理）。人和 agent 一起商讨决策：根据 issue、记忆、磁盘上的状态，拍板后再下发给框架。像现在主人和 Claude 做这个项目的方式。
3. 契约的填写权在协调层：manifest 的方向、预算、统计门、验收判据，只有人和协调 agent 拍板后才能往里填。框架只读，并证明运行中没被改。
4. 框架从"决策与校验"降为"诚实执行的基底"：阶段变成协调层可单独调用的能力，每条 `ai4sci` 子命令只跑一个能力，跑完写状态退出。不连跑、不回退、不等人；串联、回退、停止都是协调层的决定（P-10）。
5. 人在协调层的对话里，不是框架的功能。full-auto / gate-only 与文件通道从 0.2.0 移除；无人值守时的异步通道另议。
6. 协调层与执行层都是集成进来的 coding agent，都不手搓，各自可换：Claude Code 协调 + Claude Code 执行，或 Codex 协调 + Claude Code 执行，框架不改。具体 CLI 开工时定。
7. 两套 skill 物理隔离：协调层的 skill（怎么当科研助理、怎么驱动框架）跟项目走，放内仓 `coordinator/`；执行层的 skill（怎么在这个领域做实验）跟领域包走。执行层会话的搜索路径里没有协调层的目录（P-11）。
8. 主人强调的三个好处：人的角色不可替代也不应被替代；协调 agent 是人的助理，帮人头脑风暴和大规模收集；两层解耦后模块替换非常灵活。
9. spec 不转 aligned：它是滚动的，第 n 步的 spec 只驱动第 n+1 步的执行，没有更硬的理由驱动更后面的执行。敏捷：一直在变才是唯一不变的。

## 待办

- [x] 纲领四份、spec、vision、CHANGELOG 按四层改写，决策 issue [#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)，Q-10 [#19](https://github.com/zephyr4123/TJU-AI4Science/issues/19)
- [ ] 拍 Q-5 [#12](https://github.com/zephyr4123/TJU-AI4Science/issues/12) 玩具任务
- [ ] 开工：拆 #3 #4 #5 的 sub-issue，R-1 spike 与剧本后端两条线并行
