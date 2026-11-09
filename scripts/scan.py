"""在本地复现 plugins.qgis.org 的安全扫描

plugins.qgis.org 会在插件包上传后解压 ZIP，并用 Bandit 等工具检查。
这里使用与网站相同的 Bandit 规则子集（见 QGIS-Plugins-Website 仓库的
qgis-app/plugins/management/commands/data/bandit_rules.json），外加同样的
文件检查（隐藏文件、可执行文件、Python 文件权限）。

网站的 detect-secrets 和 flake8 检查未包含在内。

用法:
    uv run ./scripts/scan.py                  # 扫描 tianditu_tools/ 源码目录
    uv run ./scripts/scan.py dist/xxx.zip     # 扫描打包产物，与上传的包一致
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

DEFAULT_TARGET = "tianditu_tools"

# 与网站扫描器启用的规则一致；B111、B320 在当前 Bandit 中已不存在
BANDIT_TESTS = (
    "B101",
    "B102",
    "B103",
    "B104",
    "B105",
    "B106",
    "B107",
    "B108",
    "B110",
    "B112",
    "B113",
    "B201",
    "B202",
    "B301",
    "B302",
    "B303",
    "B304",
    "B305",
    "B306",
    "B307",
    "B308",
    "B310",
    "B311",
    "B312",
    "B313",
    "B314",
    "B315",
    "B316",
    "B317",
    "B318",
    "B319",
    "B321",
    "B323",
    "B324",
    "B401",
    "B402",
    "B403",
    "B405",
    "B406",
    "B407",
    "B408",
    "B409",
    "B412",
    "B413",
    "B501",
    "B502",
    "B503",
    "B504",
    "B505",
    "B506",
    "B507",
    "B508",
    "B509",
    "B601",
    "B602",
    "B603",
    "B604",
    "B605",
    "B606",
    "B607",
    "B608",
    "B609",
    "B610",
    "B611",
    "B612",
    "B613",
    "B614",
    "B615",
    "B701",
    "B702",
    "B703",
    "B704",
)

# 与网站扫描器一致：允许出现的工具配置文件和可疑扩展名
HIDDEN_ALLOWLIST = {
    ".gitignore",
    ".gitattributes",
    ".bandit",
    ".secrets.baseline",
    ".flake8",
}
SUSPICIOUS_SUFFIXES = (".exe", ".dll", ".so", ".dylib", ".bat", ".sh", ".ps1", ".cmd")


def parse_args():
    parser = argparse.ArgumentParser(
        description="本地复现 plugins.qgis.org 的插件安全扫描"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=DEFAULT_TARGET,
        help=f"源码目录或打包好的 zip（默认 {DEFAULT_TARGET}）",
    )
    return parser.parse_args()


def find_bandit():
    bandit = shutil.which("bandit")
    if not bandit:
        raise SystemExit("未找到 bandit，请先运行 uv sync 安装开发依赖")
    return bandit


def run_bandit(target):
    result = subprocess.run(
        [
            find_bandit(),
            "-r",
            str(target),
            "-f",
            "json",
            "--quiet",
            "-t",
            ",".join(BANDIT_TESTS),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # 即使发现问题，Bandit 也会以退出码 1 结束，但仍输出 JSON
    if not result.stdout.strip():
        raise SystemExit(f"Bandit 未返回结果：{result.stderr.strip()}")
    return json.loads(result.stdout).get("results", [])


def display_path(filename, root):
    try:
        return Path(filename).resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return Path(filename).name


def check_package(path):
    """检查 zip 内的隐藏文件、可疑扩展名和文件权限，对应网站的文件检查"""
    issues = []
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            name = info.filename
            if info.is_dir():
                continue
            base = Path(name).name
            if base.startswith(".") and base not in HIDDEN_ALLOWLIST:
                issues.append(f"{name}：隐藏文件")
            if base.lower().endswith(SUSPICIOUS_SUFFIXES):
                issues.append(f"{name}：可执行或二进制文件")
            # external_attr 的高 16 位是 Unix 权限
            if info.external_attr >> 16 & 0o111 and name.endswith(".py"):
                issues.append(f"{name}：Python 文件带可执行权限")
    return issues


def main():
    args = parse_args()
    target = Path(args.target)
    if not target.exists():
        raise SystemExit(f"找不到 {target}")

    is_zip = target.is_file() and target.suffix.lower() == ".zip"
    with tempfile.TemporaryDirectory() as tmp:
        if is_zip:
            with zipfile.ZipFile(target) as zf:
                zf.extractall(tmp)
            scan_root = Path(tmp)
            print(f"扫描打包产物：{target}")
        else:
            scan_root = target
            print(f"扫描源码目录：{target}")

        py_files = sum(1 for _ in scan_root.rglob("*.py"))
        print(f"Bandit 规则 {len(BANDIT_TESTS)} 条，Python 文件 {py_files} 个")

        issues = run_bandit(scan_root)
        if issues:
            print(f"\nBandit 发现 {len(issues)} 个问题：")
            for issue in issues:
                print(
                    f"  {display_path(issue['filename'], scan_root)}:"
                    f"{issue['line_number']} [{issue['test_id']}] "
                    f"{issue['issue_severity']} {issue['issue_text']}"
                )
        else:
            print("\nBandit 未发现问题")

        file_issues = check_package(target) if is_zip else []
        if file_issues:
            print(f"\n文件检查发现 {len(file_issues)} 个问题：")
            for issue in file_issues:
                print(f"  {issue}")

    total = len(issues) + len(file_issues)
    if total:
        print(f"\n共 {total} 个问题")
        return 1
    print("\n扫描通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
