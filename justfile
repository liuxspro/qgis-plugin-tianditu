# 默认 recipe：列出所有可用命令
default:
    @just --list
# 运行 Pylint 代码检查
lint:
    @echo 'Run Pylint...'
    @uv run pylint $(git ls-files '*.py' ':(exclude)tianditu_tools/ui/')
# 本地复现 plugins.qgis.org 的安全扫描（默认扫源码，可传入 dist 下的 zip）
scan target="tianditu_tools":
    @uv run ./scripts/scan.py {{ target }}
# 运行测试（待添加测试用例）
test:
    @echo 'No tests yet.'
# 构建 UI：将 .ui 文件编译为 .py，并做 QGIS 兼容替换
# 说明：.ui 统一使用 Qt5 风格的枚举（如 Qt::Horizontal），
# pyuic5 与 pyuic6 都能解析，因此不再维护单独的 Qt5 版 .ui 文件。
build:
    @echo 'Build UI...'
    @uv run pyuic5 ./tianditu_tools/ui/setting.ui -o ./tianditu_tools/ui/setting_5.py
    @uv run pyuic5 ./tianditu_tools/ui/mapmanager.ui -o ./tianditu_tools/ui/mapmanager_5.py
    @uv run pyuic5 ./tianditu_tools/ui/search.ui -o ./tianditu_tools/ui/search_5.py
    @uv run pyuic5 ./tianditu_tools/ui/sd.ui -o ./tianditu_tools/ui/sd_5.py
    @# QT6
    @uv run pyuic6 ./tianditu_tools/ui/setting.ui -o ./tianditu_tools/ui/setting.py
    @uv run pyuic6 ./tianditu_tools/ui/mapmanager.ui -o ./tianditu_tools/ui/mapmanager.py
    @uv run pyuic6 ./tianditu_tools/ui/search.ui -o ./tianditu_tools/ui/search.py
    @uv run pyuic6 ./tianditu_tools/ui/sd.ui -o ./tianditu_tools/ui/sd.py
    @uv run ./scripts/update_ui.py
    # Done
# 打包插件（依赖 build）
pack: build
    @echo 'Pack plugin...'
    @uv run ./scripts/pack.py
# 打包开发版（版本号追加 -dev-<短 SHA>，依赖 build）
pack-dev: build
    @echo 'Pack dev plugin...'
    @uv run ./scripts/pack.py --dev
# 校验 metadata / pyproject / uv.lock 版本一致
version-check:
    @uv run ./scripts/version.py check
# 更新版本号（同时更新 pyproject、metadata、uv.lock）
bump version:
    @uv run ./scripts/version.py bump {{ version }}
# 清理构建产物和缓存
clean:
    @echo 'Clean dist and __pycache__...'
    @rm -rf dist
    @find . -type d -name '__pycache__' -exec rm -rf {} +
# 获取地图数据
getmap:
    @echo 'Get map data...'
    @uv run ./scripts/get_maps.py
# 打包图源：将 maps/*.json 打包为 zip
packmap:
    @echo 'Pack map sources...'
    @uv run ./scripts/package_maps.py
