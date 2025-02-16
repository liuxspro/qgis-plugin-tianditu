uv run pyuic5 ./tianditu_tools/ui/setting.ui -o ./tianditu_tools/ui/setting.py
uv run pyuic5 ./tianditu_tools/ui/search.ui -o ./tianditu_tools/ui/search.py
uv run pyuic5 ./tianditu_tools/ui/sd.ui -o ./tianditu_tools/ui/sd.py

uv run pyuic6 ./tianditu_tools/ui/setting.ui -o ./tianditu_tools/ui/setting_6.py
uv run pyuic6 ./tianditu_tools/ui/search.ui -o ./tianditu_tools/ui/search_6.py
uv run pyuic6 ./tianditu_tools/ui/sd.ui -o ./tianditu_tools/ui/sd_6.py
uv run update_ui.py
uv run pack.py