# 本地与 CI 共用的入口：CI 跑的就是 `make check`，提交前本地跑一遍，审的和跑的是同一套。
.PHONY: check doctor changelog hygiene release

check: doctor changelog hygiene    ## 全部门禁

doctor:                            ## manifest 合法性 / .gitignore 挡位 / 内仓 clone 态 / remote 一致性
	./repos doctor

changelog:                         ## CHANGELOG.md 格式校验
	.github/scripts/changelog.sh check

hygiene:                           ## 外层零业务代码、无大文件
	.github/scripts/hygiene.sh

release:                           ## make release VERSION=0.2.0 → 轮转 CHANGELOG、提交、打 tag（不 push）
	.github/scripts/release.sh $(VERSION)
