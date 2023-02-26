import os
import sys
from tkinter import *
import toml, json
import argparse

settings = {}

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--title')
    parser.add_argument('--path')
    parser.add_argument('--window_size')
    args = parser.parse_args()
    return args

def get_settings_path():
    # Check if the script is running from a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Return the path to the bundled settings.toml
        return os.path.join(sys._MEIPASS, 'settings.toml')
    else:
        # Return the path to the settings.toml in the source directory
        return os.path.abspath(os.path.join(os.path.dirname(__file__), 'settings.toml'))

def get_settings():
    toml_settings = {}
    try:
        with open(get_settings_path(), 'r') as f:
            toml_settings = toml.load(f)
            return toml_settings
    except FileNotFoundError:
        return toml_settings

def get_pyinstaller_settings():
    installer_settings = {}
    for arg in sys.argv:
        if arg.startswith('--title='):
            installer_settings['title'] = arg.split('=')[1]
            return {'title': title}
        elif arg.startswith('--path='):
            installer_settings['path'] = arg.split('=')[1]
            return {'path': path}
        elif arg.startswith('--window_size='):
            installer_settings['window_size'] = arg.split('=')[1]
            return {'window_size': window_size}
    return installer_settings


args = get_args()
toml_settings = get_settings()
pyinstaller_settings = get_pyinstaller_settings()

title = args.title or pyinstaller_settings.get('title') or toml_settings.get('title') or 'Toml Editor'
path = args.path or pyinstaller_settings.get('path') or toml_settings.get('path') or 'settings.toml'
window_size = args.window_size or pyinstaller_settings.get('window_size') or toml_settings.get('window_size') or '600x900'

print(f"title: {title}, path: {path}, window_size: {window_size}")

# Read the list of settings from a TOML file
print(f"path: {path}")
with open(path, "r") as f:
    if path.endswith('.toml'):
        config = toml.load(f)
    elif path.endswith('.json'):
        config = json.load(f)

root = Tk()
root.title(title)
# use window_size or 450x900 as default
root.geometry(window_size)

# Create a frame to hold the canvas and settings
frame = Frame(root)

# Create a canvas to hold the settings
canvas = Canvas(frame)

scrollbar = Scrollbar(canvas, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame inside the canvas to hold the settings
inner_frame = Frame(scrollable_frame)
inner_frame.pack(side="top", fill="both")

# Add the settings to the inner frame and track changes
# Add the settings to the inner frame and track changes
fields = {}
def render_settings(current_settings, current_fields, parent_frame):
    row = 0
    for key, value in current_settings.items():
        if isinstance(value, dict):
            current_fields[key] = {}
            # If the value is a table, create a new section
            section_frame = LabelFrame(parent_frame, text=key)
            section_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            render_settings(value, current_fields[key], section_frame)
            row += 1
        else:
            # Otherwise, create a label and an entry field for the setting
            label = Label(parent_frame, text=key)
            label.grid(row=row, column=0, sticky="w", padx=5, pady=5)

            if isinstance(value, bool):
                var = BooleanVar(value=value)
                checkbox = Checkbutton(parent_frame, variable=var)
                checkbox.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                current_settings[key] = var
                current_fields[key] = var.get()
                checkbox.bind("<Button-1>", lambda event, key=key: current_fields.__setitem__(key, not current_settings[key].get()))
            elif isinstance(value, (int, float)):
                var = StringVar(value=str(value))
                entry = Entry(parent_frame, textvariable=var, width=20)
                entry.config(validate="key", validatecommand=(root.register(validate_number_input), '%P'))
                entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                current_settings[key] = var
                current_fields[key] = eval(var.get())
                entry.bind("<KeyRelease>", lambda event, key=key: current_fields.__setitem__(key, eval(current_settings[key].get())))
            # else if array
            elif isinstance(value, list):
                current_fields[key] = value
                text = Text(parent_frame, width=50, height=len(value))
                text.grid(row=row,   column=1, sticky="w", padx=5, pady=5)

                # insert each item in the list on a separate line
                for item in value:
                    text.insert(END, item)
                    text.insert(END, "\n")

                # function to update the list when the user edits it
                def update_list(event, key):
                    # get the edited list from the Text widget
                    edited_list = text.get("1.0", END).strip().split("\n")

                    # update the current_fields dictionary with the edited list
                    current_fields[key] = edited_list

                text.bind("<KeyRelease>", lambda event, key=key: update_list(event, key))
            else:
                # set height based on number of characters plus some padding
                height = int(len(value) / 40) + 1


                current_fields[key] = value
                text = Text(parent_frame, width=50, height=height)
                text.insert(END, value)
                text.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                text.bind("<KeyRelease>", lambda event, key=key: current_fields.__setitem__(key, text.get("1.0", END).strip()))

            row += 1


def validate_number_input(input_value):
    # Allow empty input
    if input_value == "":
        return True

    # Try to convert input to a number
    try:
        float(input_value)
    except ValueError:
        # Input is not a number
        return False

    return True

render_settings(config, fields, inner_frame)

frame.pack(side="top", fill="both", expand=True)
canvas.pack(side="top", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Create a save button to update the TOML file
def save():
    with open(path, "w") as f:
        if path.endswith('.toml'):
            toml.dump(fields, f)
        elif path.endswith('.json'):
            json.dump(fields, f, indent=4)
        else:
            raise Exception("Invalid file type")

# Create a frame to hold the save button
button_frame = Frame(frame)
button_frame.pack(side="bottom", pady=10)

save_button = Button(button_frame, text="Save", command=save)
save_button.pack()

root.mainloop()