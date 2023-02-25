import os
import sys
from tkinter import *
import pkg_resources
import toml


def get_settings_path():
    # Check if the script is running from a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Return the path to the bundled settings.toml
        return os.path.join(sys._MEIPASS, 'settings.toml')
    else:
        # Return the path to the settings.toml in the source directory
        return os.path.abspath(os.path.join(os.path.dirname(__file__), 'settings.toml'))

# Load the settings from the TOML file
with open(get_settings_path(), 'r') as f:
    settings = toml.load(f)

# Read the list of settings from a TOML file
with open(settings["path_to_config"], "r") as f:
    config = toml.load(f)

root = Tk()
root.title(settings["title"])
root.geometry(settings["window_size"])

from tkinter import *

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
                var = StringVar(value=str(value))
                entry = Entry(parent_frame, textvariable=var, width=50)
                entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                current_settings[key] = var
                current_fields[key] = eval(var.get())
                entry.bind("<KeyRelease>", lambda event, key=key: current_fields.__setitem__(key, eval(current_settings[key].get())))
            else:
                var = StringVar(value=value)
                entry = Entry(parent_frame, textvariable=var, width=50)
                entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                current_settings[key] = var
                current_fields[key] = var.get()
                entry.bind("<KeyRelease>", lambda event, key=key: current_fields.__setitem__(key, current_settings[key].get()))

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
    with open(settings["path_to_config"], "w") as f:
        toml.dump(fields, f)

# Create a frame to hold the save button
button_frame = Frame(frame)
button_frame.pack(side="bottom", pady=10)

save_button = Button(button_frame, text="Save", command=save)
save_button.pack()

root.mainloop()