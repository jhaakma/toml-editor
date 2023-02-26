# Toml Editor

This is a simple editor for config files written in [TOML](https://toml.io).

## Requirements:
- Python >=3
- Pip

## Settings.toml
The `settings.toml` file allows you to customise your TOML Editor, and has the following settings:

* `title` - The title of the window
* `path_to_config` - The path to the config file to be edited, relative to the script or compiled exe
* `window_size` - The intial size of the window

## Running with arguments

You can run the script directly with arguments like so:
    py toml-editor.py --title "Title" --path "path-to-file.toml" --window-size 800x600

Or compile it with arguments like this
    py compile.py --name "Name of EXE" --title "Title" --path "path-to-file.toml" --window-size 800x600

## Running Locally
- Run `build.sh` to install dependencies
- Run `run.sh` to run the script
- Run `compile.py` to create a standalone executable file