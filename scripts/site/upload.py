"""官网（#293）的图片与视频上 COS，打印 CDN 地址填进网站仓的 content/site.json。

跑法（外层仓根；凭据经 withkey 按需加载，桶名不进仓库，从环境变量给）：
  zsh -lic 'withkey tencentcloud env COS_BUCKET=<桶名-APPID> COS_REGION=ap-shanghai \\
    ~/.venvs/tencent/bin/python scripts/site/upload.py'

做什么：
- 本机 materials/site/out/ 下的 *.jpg / *.mp4 传到 ai4science/v1/site/{image,video}/<名>.<sha256 前 8 位>.<扩展名>。
  CDN 缓存是 immutable，内容变了 URL 跟着变。这个前缀在防盗链白名单的 /ai4science/v1 里。
- 桶里已有同名对象就跳过；前缀下不在本次清单里的旧版本删掉（只删 site/ 前缀，桶里别的不碰）。
- 打印 名字 → URL 的 JSON，与本次新传的 URL（交给 tccli cdn PushUrlsCache 预热）。
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from qcloud_cos import CosConfig, CosS3Client

ROOT = Path(__file__).parents[2]
SRC = ROOT / "materials/site/out"
PREFIX = "ai4science/v1/site/"
CDN = "https://media.zephyrxiang.com/"
TYPES = {".jpg": ("image", "image/jpeg"), ".mp4": ("video", "video/mp4")}
HEADERS = {"CacheControl": "public, max-age=31536000, immutable", "ACL": "public-read"}


def key_of(path: Path) -> str:
    kind, _ = TYPES[path.suffix]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
    return f"{PREFIX}{kind}/{path.stem}.{digest}{path.suffix}"


def main() -> None:
    bucket, region = os.environ.get("COS_BUCKET"), os.environ.get("COS_REGION")
    sid, skey = os.environ.get("TENCENTCLOUD_SECRET_ID"), os.environ.get("TENCENTCLOUD_SECRET_KEY")
    if not all([bucket, region, sid, skey]):
        raise SystemExit("缺环境变量：COS_BUCKET、COS_REGION、TENCENTCLOUD_SECRET_ID / KEY（用 withkey tencentcloud 喂）")
    cos = CosS3Client(CosConfig(Region=region, SecretId=sid, SecretKey=skey))

    files = sorted(p for p in SRC.iterdir() if p.suffix in TYPES)
    if not files:
        raise SystemExit(f"{SRC} 里没有 jpg / mp4")
    wanted = {f: key_of(f) for f in files}

    existing: set[str] = set()
    marker = ""
    while True:
        page = cos.list_objects(Bucket=bucket, Prefix=PREFIX, Marker=marker, MaxKeys=1000)
        existing |= {o["Key"] for o in page.get("Contents", [])}
        if page.get("IsTruncated") != "true":
            break
        marker = page["NextMarker"]

    fresh = []
    for path, key in wanted.items():
        if key in existing:
            continue
        cos.upload_file(Bucket=bucket, Key=key, LocalFilePath=str(path), ContentType=TYPES[path.suffix][1], **HEADERS)
        size = int(cos.head_object(Bucket=bucket, Key=key)["Content-Length"])
        if size != path.stat().st_size:
            raise SystemExit(f"{key} 上传后大小对不上：{size} != {path.stat().st_size}")
        fresh.append(CDN + key)

    stale = existing - set(wanted.values())
    for key in sorted(stale):
        cos.delete_object(Bucket=bucket, Key=key)

    print(json.dumps({p.stem: CDN + k for p, k in wanted.items()}, ensure_ascii=False, indent=2))
    print(f"新传 {len(fresh)} 个，删旧版本 {len(stale)} 个")
    for url in fresh:
        print(url)


if __name__ == "__main__":
    main()
