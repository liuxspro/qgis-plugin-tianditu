# 默认 recipe：列出所有可用命令
default:
    @just --list

# 运行 Pylint 代码检查
lint:
    @echo 'Run Pylint...'
    @uv run pylint $(git ls-files '*.py' ':(exclude)tianditu_tools/ui/')

# 运行测试（待添加测试用例）
test:
    @echo 'No tests yet.'

# 构建 UI：将 .ui 文件编译为 .py，并做 QGIS 兼容替换
build:
    @echo 'Build UI...'
    @uv run pyuic5 ./tianditu_tools/ui/setting.ui -o ./tianditu_tools/ui/setting.py
    @uv run pyuic5 ./tianditu_tools/ui/search.ui -o ./tianditu_tools/ui/search.py
    @uv run pyuic5 ./tianditu_tools/ui/sd.ui -o ./tianditu_tools/ui/sd.py
    @uv run pyuic6 ./tianditu_tools/ui/setting.ui -o ./tianditu_tools/ui/setting_6.py
    @uv run pyuic6 ./tianditu_tools/ui/search.ui -o ./tianditu_tools/ui/search_6.py
    @uv run pyuic6 ./tianditu_tools/ui/sd.ui -o ./tianditu_tools/ui/sd_6.py
    @uv run ./scripts/update_ui.py

# 打包插件（依赖 build）
pack: build
    @echo 'Pack plugin...'
    @uv run ./scripts/pack.py

# 清理构建产物和缓存
clean:
    @echo 'Clean dist and __pycache__...'
    @rm -rf dist
    @find . -type d -name '__pycache__' -exec rm -rf {} +

# 获取地图数据
getmap:
    @echo 'Get map data...'
    @uv run ./scripts/get_maps.py
