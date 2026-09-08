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

html: $(VENV)/.stamp               ## research/ 下全部 .md → 同目录 .html（README.md → index.html；含文内链接检查）
	$(VENV)/bin/python $(MD2HTML)/md2html.py build --all

html-check: html                   ## html 必须与 md 同步：重建后 research/ 下的 .html 不能有未暂存的改动或未追踪文件（暂存过的算同步，本地提交前也能过）
	@bad=$$(git diff --name-only -- 'research/**/*.html' 'research/*.html'; git ls-files --others --exclude-standard -- research | grep '\.html$$' || true); \
	if [ -n "$$bad" ]; then echo "✗ html 与 md 不同步，跑 make html 后把这些文件一起 git add："; echo "$$bad" | sed 's/^/    /'; exit 1; fi; \
	echo "✓ html 与 md 同步"

release:                           ## make release VERSION=0.2.0 → 轮转 CHANGELOG、提交、打 tag（不 push）
	.github/scripts/release.sh $(VERSION)
