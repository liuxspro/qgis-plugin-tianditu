from pathlib import Path

cwd = Path.cwd()
ui_dir = cwd.joinpath("tianditu_tools/ui")


def update_ui_genate_py(file_path: Path):
    assert file_path.suffix == ".py"
    content = file_path.read_text(encoding="utf-8")
    content = content.replace("from PyQt5", "from qgis.PyQt")
    content = content.replace("from PyQt6", "from qgis.PyQt")
    file_path.write_text(content, encoding="utf-8")


def update_file():
    # 遍历目录下的所有 .py 文件
    for file_path in ui_dir.glob("**/*.py"):
        print(f"正在处理文件: {file_path}")
        try:
            update_ui_genate_py(file_path)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"处理文件 {file_path} 时出错: {e}")


update_file()
