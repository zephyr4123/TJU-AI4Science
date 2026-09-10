# adr/ 放什么

ADR（Architecture Decision Record，架构决策记录）：一个决定一个文件，写背景、选项、决定、后果；**只追加不修改**，要推翻就新开一条注明取代第 N 条，目的是留住"当时为什么这么定"。

这里只放**仓库基础设施**的决定：拓扑、版本与发布、CI 门禁这类一旦改动会影响所有人工作方式的事。

产品架构不在这里。产品架构是可改的总纲领，在 [`../architecture/`](../architecture/README.md)，每个文件末尾的变更记录承担 ADR 留轨迹的职能。

| 编号 | 决定 | 状态 |
|---|---|---|
| [0001](0001-nested-git-topology.md) | 外层协作仓 + 内仓生产 monorepo（nested-git） | 已采纳 |
| [0002](0002-versioning-and-release.md) | 版本、变更日志与发布流水线 | 已采纳 |
