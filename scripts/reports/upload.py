"""汇报页（research/reports/）用的图片与视频上 COS，打印 CDN 地址填进那份 HTML。

汇报页是进 git 的单文件 HTML，图和视频不进仓（红线：单文件 2 MB），走 CDN 引用。

跑法（外层仓根；凭据经 withkey 按需加载，桶名不进仓库，从环境变量给）：
  zsh -lic 'withkey tencentcloud env COS_BUCKET=<桶名-APPID> COS_REGION=ap-shanghai \\
    ~/.venvs/tencent/bin/python scripts/reports/upload.py 2026-1012-progress'

做什么：
- 本机 materials/reports/<报告名>/out/ 下的 *.jpg / *.mp4 传到 ai4science/v1/reports/<报告名>/<名>.<sha256 前 8 位>.<扩展名>。
  CDN 缓存是 immutable，内容变了 URL 跟着变。这个前缀在防盗链白名单的 /ai4science/v1 里。
- 桶里已有同名对象就跳过。旧版本不删：汇报页发出去就不再改，历史版本的页面还引用着它们。
- 打印 名字 → URL 的 JSON，与本次新传的 URL（交给 tccli cdn PushUrlsCache 预热）。
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

from qcloud_cos import CosConfig, CosS3Client

ROOT = Path(__file__).parents[2]
CDN = "https://media.zephyrxiang.com/"
TYPES = {".jpg": "image/jpeg", ".mp4": "video/mp4"}
HEADERS = {"CacheControl": "public, max-age=31536000, immutable", "ACL": "public-read"}


def key_of(prefix: str, path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
    return f"{prefix}{path.stem}.{digest}{path.suffix}"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("用法：upload.py <报告名>（materials/reports/ 下的目录名）")
    report = sys.argv[1]
    src = ROOT / "materials/reports" / report / "out"
    prefix = f"ai4science/v1/reports/{report}/"
    bucket, region = os.environ.get("COS_BUCKET"), os.environ.get("COS_REGION")
    sid, skey = os.environ.get("TENCENTCLOUD_SECRET_ID"), os.environ.get("TENCENTCLOUD_SECRET_KEY")
    if not all([bucket, region, sid, skey]):
        raise SystemExit("缺环境变量：COS_BUCKET、COS_REGION、TENCENTCLOUD_SECRET_ID / KEY（用 withkey tencentcloud 喂）")
    if not src.is_dir():
        raise SystemExit(f"没有这个目录：{src}")
    files = sorted(p for p in src.iterdir() if p.suffix in TYPES)
    if not files:
        raise SystemExit(f"{src} 里没有 jpg / mp4")
    cos = CosS3Client(CosConfig(Region=region, SecretId=sid, SecretKey=skey))
    wanted = {f: key_of(prefix, f) for f in files}

    existing: set[str] = set()
    marker = ""
    while True:
        page = cos.list_objects(Bucket=bucket, Prefix=prefix, Marker=marker, MaxKeys=1000)
        existing |= {o["Key"] for o in page.get("Contents", [])}
        if page.get("IsTruncated") != "true":
            break
        marker = page["NextMarker"]

    fresh = []
    for path, key in wanted.items():
        if key in existing:
            continue
        cos.upload_file(Bucket=bucket, Key=key, LocalFilePath=str(path), ContentType=TYPES[path.suffix], **HEADERS)
        size = int(cos.head_object(Bucket=bucket, Key=key)["Content-Length"])
        if size != path.stat().st_size:
            raise SystemExit(f"{key} 上传后大小对不上：{size} != {path.stat().st_size}")
        fresh.append(CDN + key)

    print(json.dumps({p.name: CDN + k for p, k in wanted.items()}, ensure_ascii=False, indent=2))
    print(f"新传 {len(fresh)} 个，已有 {len(wanted) - len(fresh)} 个")
    for url in fresh:
        print(url)


if __name__ == "__main__":
    main()
