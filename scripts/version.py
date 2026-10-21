import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path

cwd = Path.cwd()
METADATA_FILE = cwd.joinpath("tianditu_tools", "metadata.txt")
PYPROJECT_FILE = cwd.joinpath("pyproject.toml")
LOCK_FILE = cwd.joinpath("uv.lock")
PROJECT_NAME = "qgis-plugin-tianditu"

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
METADATA_VERSION_RE = re.compile(r"(?m)^version=(.*)$")
METADATA_VERSION_LINE_RE = re.compile(r"(?m)^version=.*$")
PYPROJECT_VERSION_LINE_RE = re.compile(r'(?m)^version\s*=\s*"[^"]+"')


def read_metadata_version():
    match = METADATA_VERSION_RE.search(METADATA_FILE.read_text(encoding="utf-8"))
    if not match:
        raise SystemExit(f"未在 {METADATA_FILE} 中找到 version")
    return match.group(1).strip()


def read_pyproject_version():
    data = tomllib.loads(PYPROJECT_FILE.read_text(encoding="utf-8"))
    return data["project"]["version"]


def read_lock_version():
    data = tomllib.loads(LOCK_FILE.read_text(encoding="utf-8"))
    for package in data.get("package", []):
        if package.get("name") == PROJECT_NAME:
            return package.get("version", "")
    raise SystemExit(f"未在 {LOCK_FILE} 中找到 {PROJECT_NAME}")


def check_versions(tag=None):
    versions = {
        "metadata.txt": read_metadata_version(),
        "pyproject.toml": read_pyproject_version(),
        "uv.lock": read_lock_version(),
    }
    if len(set(versions.values())) > 1:
        print("版本不一致：")
        for name, value in versions.items():
            print(f"  {name:<16}{value}")
        print("\n运行 `just bump <version>` 修复。")
        return 1
    version = versions["pyproject.toml"]
    if not VERSION_RE.match(version):
        print(f"版本号格式不符合 x.y.z：{version}")
        return 1
    if tag is not None and tag != f"v{version}":
        print(f"tag {tag} 与版本 {version} 不一致，应为 v{version}")
        return 1
    print(f"版本一致：{version}")
    return 0


def replace_once(path, pattern, replacement):
    text = path.read_text(encoding="utf-8")
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"未在 {path} 中找到可替换的版本行")
    path.write_text(text, encoding="utf-8")


def bump_version(version):
    if not VERSION_RE.match(version):
        raise SystemExit(f"版本号格式不符合 x.y.z：{version}")
    replace_once(PYPROJECT_FILE, PYPROJECT_VERSION_LINE_RE, f'version = "{version}"')
    replace_once(METADATA_FILE, METADATA_VERSION_LINE_RE, f"version={version}")
    try:
        subprocess.run(["uv", "lock"], check=True, cwd=cwd)
    except FileNotFoundError as exc:
        raise SystemExit("未找到 uv，请先安装 uv") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"uv lock 执行失败：{exc}") from exc
    print(f"版本已更新为 {version}，请记得补充 changelog")


def main():
    parser = argparse.ArgumentParser(description="同步 QGIS 插件版本号")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check_parser = subparsers.add_parser("check", help="校验版本一致性")
    check_parser.add_argument("--tag", help="同时校验 git tag，例如 v0.6.0")
    bump_parser = subparsers.add_parser("bump", help="更新版本号")
    bump_parser.add_argument("version", help="新版本号，例如 0.6.1")
    args = parser.parse_args()

    if args.command == "check":
        return check_versions(args.tag)
    bump_version(args.version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
