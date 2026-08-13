import re

with open("sherlock_project/gui.py", "r") as f:
    lines = f.readlines()

new_lines = []
in_dox_tab = False
for line in lines:
    if "def create_dox_tab(self):" in line:
        in_dox_tab = True
        new_lines.append(line)
        continue

    if in_dox_tab and "def " in line:
        in_dox_tab = False

    if in_dox_tab and "self.text_dox_results = ctk.CTkTextbox(results_panel" in line:
        new_lines.append(line)
        new_lines.append("        self.filter_panel = ctk.CTkFrame(results_panel, width=200)\n")
        new_lines.append("        self.filter_panel.grid(row=0, column=1, sticky=\"ns\", padx=5, pady=15)\n")
        new_lines.append("        ctk.CTkLabel(self.filter_panel, text=\"Live Filters\", font=ctk.CTkFont(weight=\"bold\")).pack(pady=10)\n")
        new_lines.append("        self.filter_checkboxes = {}\n")
        continue

    new_lines.append(line)

with open("sherlock_project/gui.py", "w") as f:
    f.writelines(new_lines)
