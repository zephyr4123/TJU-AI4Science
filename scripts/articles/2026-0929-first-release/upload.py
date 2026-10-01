"""公众号稿（#193）的配图上 COS，正文改用 CDN 链接。

跑法（外层仓根；凭据经 withkey 按需加载，桶名不进仓库，从环境变量给）：
  zsh -lic 'withkey tencentcloud env COS_BUCKET=<桶名-APPID> COS_REGION=ap-shanghai \\
    ~/.venvs/tencent/bin/python scripts/articles/2026-0929-first-release/upload.py'

做什么：
- 本机 materials/articles/2026-0929-first-release/figures/*.png 按类型分目录：
  ui-* → screenshots/，chart-* → charts/，fig-* → diagrams/；对象名去掉类型前缀、带内容哈希
  （<名>.<sha256 前 8 位>.png）。CDN 缓存是 immutable，内容变了 URL 跟着变，旧缓存不会串。
- 桶里已有同名对象就跳过；前缀下不在本次清单里的旧版本删掉（只删本篇的前缀，桶里别的东西不碰）。
- 清单写 docs/articles/2026-0929-first-release/figures.json；正文 README.md 里的图片链接按文件名换成新 URL。
- 最后打印本次新传的 URL，交给 tccli cdn PushUrlsCache 预热。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

from qcloud_cos import CosConfig, CosS3Client

ROOT = Path(__file__).parents[3]
SRC = ROOT / "materials/articles/2026-0929-first-release/figures"
ARTICLE = ROOT / "docs/articles/2026-0929-first-release/README.md"
MANIFEST = ROOT / "docs/articles/2026-0929-first-release/figures.json"
PREFIX = "ai4science/articles/2026-0929-first-release/"
CDN = "https://media.zephyrxiang.com/"
KINDS = {"ui-": "screenshots", "chart-": "charts", "fig-": "diagrams"}
HEADERS = {"CacheControl": "public, max-age=31536000, immutable", "ACL": "public-read"}


def key_of(path: Path) -> str:
    for head, kind in KINDS.items():
        if path.name.startswith(head):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
            return f"{PREFIX}{kind}/{path.stem.removeprefix(head)}.{digest}.png"
    raise SystemExit(f"不认识的图：{path.name}（文件名要以 {'/'.join(KINDS)} 开头）")


def local_name_of(key: str) -> str:
    kind, file = key.removeprefix(PREFIX).split("/", 1)
    head = {v: k for k, v in KINDS.items()}[kind]
    return head + file.rsplit(".", 2)[0] + ".png"


def main() -> None:
    bucket, region = os.environ.get("COS_BUCKET"), os.environ.get("COS_REGION")
    sid, skey = os.environ.get("TENCENTCLOUD_SECRET_ID"), os.environ.get("TENCENTCLOUD_SECRET_KEY")
    if not all([bucket, region, sid, skey]):
        raise SystemExit("缺环境变量：COS_BUCKET、COS_REGION、TENCENTCLOUD_SECRET_ID / KEY（用 withkey tencentcloud 喂）")
    cos = CosS3Client(CosConfig(Region=region, SecretId=sid, SecretKey=skey))

    files = sorted(SRC.glob("*.png"))
    if not files:
        raise SystemExit(f"{SRC} 里没有图，先出图")
    wanted = {f.name: key_of(f) for f in files}

    existing: set[str] = set()
    marker = ""
    while True:
        page = cos.list_objects(Bucket=bucket, Prefix=PREFIX, Marker=marker, MaxKeys=1000)
        existing |= {o["Key"] for o in page.get("Contents", [])}
        if page.get("IsTruncated") != "true":
            break
        marker = page["NextMarker"]

    fresh = []
    for name, key in wanted.items():
        if key in existing:
            continue
        cos.upload_file(Bucket=bucket, Key=key, LocalFilePath=str(SRC / name), ContentType="image/png", **HEADERS)
        size = int(cos.head_object(Bucket=bucket, Key=key)["Content-Length"])
        if size != (SRC / name).stat().st_size:
            raise SystemExit(f"{key} 上传后大小对不上：{size}")
        fresh.append(CDN + key)

    stale = sorted(existing - set(wanted.values()))
    for key in stale:
        cos.delete_object(Bucket=bucket, Key=key)

    urls = {name: CDN + key for name, key in sorted(wanted.items())}
    MANIFEST.write_text(json.dumps(urls, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    text = ARTICLE.read_text(encoding="utf-8")
    pattern = re.compile(r"\]\((figures/[\w-]+\.png|" + re.escape(CDN + PREFIX) + r"[\w/.-]+\.png)\)")

    def swap(m: re.Match[str]) -> str:
        ref = m.group(1)
        name = ref.removeprefix("figures/") if ref.startswith("figures/") else local_name_of(ref.removeprefix(CDN))
        if name not in urls:
            raise SystemExit(f"正文引用了清单里没有的图：{name}")
        return f"]({urls[name]})"

    ARTICLE.write_text(pattern.sub(swap, text), encoding="utf-8")
    print(f"新传 {len(fresh)}，跳过 {len(wanted) - len(fresh)}，删旧 {len(stale)}", file=sys.stderr)
    for url in fresh:
        print(url)


if __name__ == "__main__":
    main()
