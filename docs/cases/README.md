# 案例库

真实科研案例的索引。原件不进 git（红线 3），这里只放案例卡与学长的原文；原件在本机 `materials/`，整目录被 `.gitignore` 挡住。采集入口是 [#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1)。

## 索引

| slug | 案例类型 | 任务类型 | 应用领域 | 来源 | 状态 | 喂给哪一层 |
|---|---|---|---|---|---|---|
| [lnp-lipid-design](lnp-lipid-design/) | 复现型 | 回归 | 药剂学 | 第三方论文 | 登记，0.2.0 不跑 | 验证 / 评测 |
| [boehm-stat5-petab](boehm-stat5-petab/) | 调参型 | 连续参数优化 | 系统生物学 | 第三方 benchmark | **已成任务包** `platform/tasks/boehm-nll`，run_0 均值 224.74、σ 28.8，真跑 3 轮出第一个 keep 148.26 | 实验内环 |
| [vlm-hard-negatives](vlm-hard-negatives/) | 过程访谈 | 表示学习 | 多模态 ML | 学长本人工作 | 已入库 | 协调层 |
| [rahman-ode-petab](rahman-ode-petab/) | 平台自测 | 连续参数优化 | 流行病学 | 第三方 benchmark | **已成任务包** `platform/tasks/rahman-nll`，只经 `ai4sci task design` 接入（[#41](https://github.com/zephyr4123/TJU-AI4Science/issues/41)），run_0 均值 21.5958、σ 0.056，8 轮出 1 个 keep 21.339，验证 PASS | 实验内环；接任务入口测试 |
| [gua-pinn-reproduction](gua-pinn-reproduction/) | 平台演练 | 论文复现（一级） | 计算物理 | 第三方论文 arXiv 2609.01558 | **已复现，验收已签**（2026-09-21）：两行都在论文 ±2σ 内，加 GUA 降 62.2%（论文 62.6%），代码一字未改；助理自走全链、研究者 8 句话两次签字（[#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120)） | 复现流全链 |
| [boehm-codex-drill](boehm-codex-drill/) | 平台演练 | 连续参数优化 | 系统生物学 | 第三方 benchmark（同 boehm-stat5-petab） | **验收已签**（2026-09-22）：两层都是 Codex 跑通研究流全链，基线 NLL 138.2219、三轮搜索无一过门、交付基线参数；研究者 9 句话两次签字；撞 7 个坑全修根因（5 个是 Codex 适配器的）（[#135](https://github.com/zephyr4123/TJU-AI4Science/issues/135)） | 研究流全链 + Codex 适配器 + 设置 |

## 案例卡怎么写

- **按任务类型描述，不按应用领域描述。** 我们搭的是平台，平台看到的是「9 个参数最小化一个标量」「SMILES 进、标量出」这类形状；应用领域只留一个名词，科学细节交给原文文件。
- 学长的原文一字不改落盘（`questionnaire.md` / `interview.md`），做过的转换动作写在文件开头。
- 卡上写「已成任务包 → platform/tasks/<name>」，任务包的 `manifest.yaml` 写 `case:` 指回卡。两边互相指，问「这任务哪来的」和「这案例用了没」查同一个地方。
- 原件索引必须有 sha256 与重取方式。
- 类型是字段不是目录：案例平铺，靠索引表的两列过滤。有二十个再考虑分层。

## 交付与 #1 要求的三处不符（2026-09-15 收到时记录）

1. **只有案例三是学长本人的工作。** 案例一、案例二是第三方公开论文加公开代码。#1 的案例一原本要「你自己或组里已经发表的论文」。后果：案例一的核心数字是湿实验测量值，我们拿不到原始数据，能对账的只有预测相关性。
2. **三个案例不来自同一个课题。** #1 要求同课题好让材料互相印证，实际是三个孤立的东西，跨案例对账这条路不存在。
3. **#1 写了「不用拿机器学习凑数」，三个案例里两个是机器学习。** 这是导师要求做交叉领域的结果，主人 2026-09-16 确认这是预期的，不是偏差。
