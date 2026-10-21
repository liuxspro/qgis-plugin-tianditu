import argparse
import os
import re
import shutil
import subprocess
import tomllib
import zipfile
from pathlib import Path

# Define the source and destination directories
cwd = Path.cwd()
source_dir = cwd.joinpath("tianditu_tools")
dist_dir = cwd.joinpath("dist")
# same as original plugin package name (tianditu-tools).
dist_source_dir = dist_dir.joinpath("tianditu-tools")
pyproject_file = cwd.joinpath("pyproject.toml")

# Other necessary files
other_files = ["README.md", "LICENSE"]

METADATA_VERSION_LINE_RE = re.compile(r"(?m)^version=.*$")
BASE_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def parse_args():
    parser = argparse.ArgumentParser(description="打包 QGIS 插件")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="生成开发版，版本号追加 -dev-<短 SHA>",
    )
    return parser.parse_args()


def delete_pycache(directory):
    pycache_dir = directory.joinpath("__pycache__")

    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    for subdirectory in directory.iterdir():
        if subdirectory.is_dir():
            delete_pycache(subdirectory)


def get_base_version():
    data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
    version = data["project"]["version"]
    if not BASE_VERSION_RE.match(version):
        raise SystemExit(f"pyproject.toml 中的版本号格式不符合 x.y.z：{version}")
    return version


def get_short_sha():
    result = subprocess.run(
        ["git", "rev-parse", "--short=7", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    short_sha = os.environ.get("GITHUB_SHA", "")[:7]
    if short_sha:
        return short_sha
    raise SystemExit("无法获取提交 SHA，请在 git 仓库中运行或设置 GITHUB_SHA")


def write_dist_version(version):
    metadata_file = dist_source_dir.joinpath("metadata.txt")
    content, count = METADATA_VERSION_LINE_RE.subn(
        f"version={version}",
        metadata_file.read_text(encoding="utf-8"),
        count=1,
    )
    if count != 1:
        raise SystemExit(f"未在 {metadata_file} 中找到 version 行")
    metadata_file.write_text(content, encoding="utf-8")


def pack(version):
    # 删除dist文件夹
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    # 递归删除 __pycache__ 文件夹
    delete_pycache(source_dir)
    # 复制源文件夹到 dist 目录下的 tianditu-tools 文件夹
    shutil.copytree(source_dir, dist_source_dir)
    # 删除ui文件夹的 ui 文件，只保留 python 文件
    for file_path in dist_source_dir.joinpath("ui").glob("*.ui"):
        file_path.unlink()
    # 复制 README 和 LICENSE 文件
    for file in other_files:
        shutil.copy(cwd.joinpath(file), dist_source_dir)
    # 版本号以 pyproject.toml 为准，只改写 dist 中的副本
    write_dist_version(version)
    filename = f"tianditu_tools-v{version}.zip"
    # Zip the destination directory
    with zipfile.ZipFile(
        dist_dir.joinpath(filename), "w", zipfile.ZIP_DEFLATED
    ) as zipf:
        for file in dist_source_dir.glob("**/*"):
            zipf.write(file, file.relative_to(dist_source_dir.parent))
    # 删除dist下的打包目录
    shutil.rmtree(dist_source_dir)
    print(f"完成打包 {filename}")


if __name__ == "__main__":
    args = parse_args()
    package_version = get_base_version()
    if args.dev:
        package_version = f"{package_version}-dev-{get_short_sha()}"
    pack(package_version)
