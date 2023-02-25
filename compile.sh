cd "$(dirname "$0")"
pyinstaller --onefile --add-data "settings.toml;." toml-editor.py