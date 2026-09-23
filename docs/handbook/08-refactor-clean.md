# 08 重构要干净

## 场景

要动结构：换目录布局、换配置读取方式、换一个概念的名字、删一条旧路。最容易的做法是加新的、留旧的、写个兼容层。三个月后两条路都活着，没人知道哪条是真的。

## 做法

1. **不光加不删。** 新路通了，旧入口逐个删干净：命令、环境变量、文件名、函数、页面组件、文档里的说法、测试里的路径。删的时候 grep 一遍全仓，包括文档与测试。
2. **不打补丁，改根因。** 症状在 prompt 里，根因在框架里，就改框架（见下面 #137 的 σ）。
3. **一个概念一处读取点。** 配置、路径、清单这类东西只在一个模块读，其余地方从它拿；两处读同一个文件迟早读出两个答案。
4. **旧数据一次性脚本搬，不写运行时兼容。** 脚本放外层 `scripts/oneoff/`，只搬不删，跑完记进 issue；产品代码里不留「如果是老格式就……」的分支。内测期没有兼容包袱，1.0.0 之后走弃用周期（[`CONTRIBUTING.md`「版本与发布」](../../CONTRIBUTING.md#版本与发布)）。
5. **文档与测试同一轮跟上。** 改了目录、命令、字段，文档与测试里引用它的地方在同一个 PR 里改；不改文档的重构等于没做完。
6. **每一行代码都要有存在的理由。** 顺手看见的死函数、空包、没人用的样式类、`.gitkeep` 占位，在同一逻辑单元里一起删；diff 里看得见就行，不用另立 issue。
7. **重构要彻底，但范围要有边界。** 顺手小清理限同一逻辑单元；大重构单独立项、单独一条 issue。

## 反例

- 新旧两套配置读取都保留「以防万一」：一年后两套都在读，值不一样时谁赢没人说得清。
- 环境变量改名，旧名字留着当别名：文档写新的、老脚本用旧的、agent 从代码里看到两个名字不知道用哪个。
- 目录搬了，测试里写死的旧路径「永远跳过」——测试还绿着，只是什么都没测。
- 删了功能，README 还在教人用它。

## 本仓真实例子

- 删干净：[#140](https://github.com/zephyr4123/TJU-AI4Science/issues/140) 删了内仓的空包 `tools/`、死函数 `env._run` / `outputs.touch_output` / `computes.default_name`、前端死代码与没人用的样式类；两条永远跳过的测试改指到 `projects/`（内仓 CHANGELOG「移除」「修复」）。[#142](https://github.com/zephyr4123/TJU-AI4Science/issues/142) 顺手删了外层的 `assets/` 与两个空的 `.gitkeep`。
- 旧入口退役：[#130](https://github.com/zephyr4123/TJU-AI4Science/issues/130) `AI4SCI_COORDINATOR_MODEL` / `_EFFORT` / `AI4SCI_EXECUTOR_MODEL` 三个环境变量退役，模型与深度只从 `agents.yaml` 读；老对话 meta 里的 null 一次性填成当时的缺省，没留运行时兼容。
- 一次性脚本搬数据：[#136](https://github.com/zephyr4123/TJU-AI4Science/issues/136) 旧的散装工作区搬成项目，外层 [`scripts/oneoff/migrate-workspaces-to-projects.py`](../../scripts/oneoff/migrate-workspaces-to-projects.py) 只搬不删。
- 改根因不打补丁：[#137](https://github.com/zephyr4123/TJU-AI4Science/issues/137) σ 原本由执行层自己写 `sigma.json`，算错了；修法不是在 prompt 里多叮嘱一句，而是改由框架从 `baseline/repeats/` 算，执行层不再碰它。
- 环境收纳：[#138](https://github.com/zephyr4123/TJU-AI4Science/issues/138) uv 管一切之后，旧的建环境方式、旧的路径读法一并删掉，README 分「只用」「改代码」两种人重写。
