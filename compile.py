import argparse
import os
import toml

parser = argparse.ArgumentParser()
parser.add_argument('--name', help='The name of the PyInstaller package')
parser.add_argument('--title', help='The title of the application')
parser.add_argument('--path', help='The path to the TOML file')
parser.add_argument('--window_size', help='The size of the window')
args = parser.parse_args()

name_arg = ['--name', args.name] if args.name else []
title_arg = ['--title', args.title] if args.title else []
path_arg = ['--path', args.path] if args.path else []
window_size_arg = ['--window_size', args.window_size] if args.window_size else []

# save the title, path, and window_size to a TOML file

# open existing settings file

# if no settings file exists, create one
if not os.path.exists('settings.toml'):
    with open('settings.toml', 'w+') as f:
        toml.dump({}, f)

with open('settings.toml', 'r+') as f:
    # get existing toml from file
    toml_settings = toml.load(f)
    # update the toml with the new settings
    if title_arg:
        toml_settings.update({'title': title_arg[1]})
    if path_arg:
        toml_settings.update({'path': path_arg[1]})
    if window_size_arg:
        toml_settings.update({'window_size': window_size_arg[1]})
    # clear contents and write the updated toml to the fil
    f.seek(0)
    toml.dump(toml_settings, f)

pyinstaller_cmd = ['pyinstaller', '--onefile', '--add-data', 'settings.toml;.'] + name_arg + ['toml-editor.py']

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.system(' '.join(pyinstaller_cmd))