import sys
import zipfile
from datetime import date
from pathlib import Path

cwd = Path.cwd()
maps_dir = cwd.joinpath("tianditu_tools/maps")
dist_dir = cwd.joinpath("dist")

date_str = date.today().strftime("%Y%m%d")
filename = f"map{date_str}.zip"

json_files = list(maps_dir.glob("*.json"))
if not json_files:
    print("maps 目录下没有 JSON 文件")
    sys.exit(1)

dist_dir.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(dist_dir.joinpath(filename), "w", zipfile.ZIP_DEFLATED) as zipf:
    for file in sorted(json_files):
        zipf.write(file, file.name)
        print(f"  + {file.name}")

print(f"\n完成打包 {filename}")
