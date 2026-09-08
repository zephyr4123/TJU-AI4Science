# 本地与 CI 共用的入口：CI 跑的就是 `make check`，提交前本地跑一遍，审的和跑的是同一套。
.PHONY: check doctor changelog hygiene html html-check release

VENV := .venv
MD2HTML := .github/scripts/md2html

check: doctor changelog hygiene html-check    ## 全部门禁

doctor:                            ## manifest 合法性 / .gitignore 挡位 / 内仓 clone 态 / remote 一致性
	./repos doctor

changelog:                         ## CHANGELOG.md 格式校验
	.github/scripts/changelog.sh check

hygiene:                           ## 外层零业务代码、无大文件
	.github/scripts/hygiene.sh

$(VENV)/.stamp: $(MD2HTML)/requirements.txt    ## 依赖装在项目局部 venv，钉版本
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q -r $<
	touch $@

html: $(VENV)/.stamp               ## research/*/*/README.md → 同目录 index.html（含文内链接检查）
	$(VENV)/bin/python $(MD2HTML)/md2html.py build --all

html-check: html                   ## html 必须与 md 同步：构建后 index.html 不能有改动或未追踪
	@bad=$$(git status --porcelain -- 'research/*/*/index.html'); \
	if [ -n "$$bad" ]; then echo "✗ index.html 与 README.md 不同步，跑 make html 后一起提交："; echo "$$bad"; exit 1; fi; \
	echo "✓ html 与 md 同步"

release:                           ## make release VERSION=0.2.0 → 轮转 CHANGELOG、提交、打 tag（不 push）
	.github/scripts/release.sh $(VERSION)
