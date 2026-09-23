# 执行层第一次会话（Codex，写壳，4 分钟）

命令与自述按先后；读文件都是 sed / rg 一次拼几个，9 条命令读完仓库。


> 我会先核对官方仓库的 README、Burgers 配置和训练/测试产物格式，再只写评分契约与运行封装；不会自行运行训练或修改方法。

- `"pwd && rg --files -g 'README.md' -g 'burgers.yaml' -g 'trainer.py' -g 'run_test.py' -g 'simulation_paras.py' -g 'requirements.txt' -g 'paper.md' -g 'structured`
- `"sed -n '1,240p' code/README.md && sed -n '1,260p' code/experiments/PINN/trainer.py && sed -n '1,240p' code/experiments/PINN/training_configs/burgers.yaml"`
- `"sed -n '180,380p' code/README.md && sed -n '240,520p' code/experiments/PINN/trainer.py && sed -n '1,320p' code/experiments/PINN/lib_pinns/burgers/trainer.py &&`
- `"rg -n \"write_formal_metrics|run_training|save_path|run_folder|record_update|conflict|prediction|relative_l2|final\" code/experiments/PINN/lib_pinns code/exper`
- `"sed -n '1,100p' code/experiments/PINN/lib_pinns/trainer_basis.py && sed -n '400,560p' code/experiments/PINN/lib_pinns/trainer_basis.py && sed -n '190,235p' cod`
- `"sed -n '500,700p' code/experiments/PINN/lib_pinns/trainer_basis.py && find harness -maxdepth 2 -type f -print 2>/dev/null || true && ls -la"`

> 上游入口已确认：`experiments/PINN/trainer.py` 支持 `--random-seed`，并在每次训练后写出包含独立重算的 `relative_l2` 与 `conflict.r_p` 的 `formal_metrics.json`。我将固定为 Burgers / ConFIG / 2-loss / GUA / 30,000 epochs。

- `"sed -n '1,220p' code/experiments/PINN/lib_pinns/burgers/networks.py && sed -n '1,200p' code/experiments/PINN/lib_pinns/burgers/simulation_paras.py && sed -n '1`
- `"rg -n \"def train_from_scratch|path_config_file|set_config_items\" code/experiments/PINN/lib_pinns/foxutils/trainerX.py && sed -n '520,700p' code/experiments/P`

> 论文表 8 同时给出无 GUA 的 ConFIG 对照值，因此我会把该对照也作为同一入口中的第二个官方原样运行；评分结果将同时保留两种相对 L2 误差和 GUA 后冲突率。

- `"awk 'length("'$0) > 100 {print FILENAME ":" FNR ":" length($0) ":" $0}'"' harness/launcher.sh harness/evaluate.py harness/make_run0.sh scoring.yaml && sed -n '`

> 写了 `scoring.yaml`、`harness/launcher.sh`、`harness/evaluate.py`、`harness/make_run0.sh`。  
> `code/`：没改。  
> 缺什么：无额外数据或密钥；运行需要 GPU 与已安装上游依赖。  
> 重点校验：确认 PyTorch 2.8 环境兼容，并注意平台强制的 42–46 种子与论文报告的 0–4 种子不一致。


用量：输入 718481（缓存命中 644608）、输出 11414（其中推理 5066）

