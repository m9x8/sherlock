import re

with open("sherlock_project/gui.py", "r") as f:
    content = f.read()

# Replace empty _orchestrator_result_callback
old_cb = """    def _orchestrator_result_callback(self, category, data):
        print(f"[{category.upper()}] New Result: {data}")"""

new_cb = """    def _orchestrator_result_callback(self, category, data):
        # Create filter checkbox if it doesn't exist
        if hasattr(self, 'filter_panel') and category not in self.filter_checkboxes:
            cb = ctk.CTkCheckBox(self.filter_panel, text=category.capitalize(), command=self._apply_dox_filters)
            cb.select()
            cb.pack(pady=5, anchor="w", padx=10)
            self.filter_checkboxes[category] = cb

        if not hasattr(self, 'dox_async_results'):
            self.dox_async_results = []
        self.dox_async_results.append((category, data))

        self._apply_dox_filters()

    def _apply_dox_filters(self):
        if not hasattr(self, 'text_dox_results') or not hasattr(self, 'dox_async_results'):
            return

        active_categories = [cat for cat, cb in getattr(self, 'filter_checkboxes', {}).items() if cb.get()]

        self._clear_textbox(self.text_dox_results)
        # Redisplay base results if they exist
        if hasattr(self, 'dox_results'):
            for category, items in self.dox_results.items():
                self._insert_text(self.text_dox_results, f"[ {category.upper()} ]\\n")
                if not items:
                    self._insert_text(self.text_dox_results, " Geen vermeldingen gevonden.\\n\\n")
                else:
                    for item in items:
                        self._insert_text(self.text_dox_results, f"• {item['title']}\\n  Link: {item['url']}\\n\\n")

        self._insert_text(self.text_dox_results, "\\n[ ASYNC DEEP INTEL ]\\n")
        for cat, data in self.dox_async_results:
            if not active_categories or cat in active_categories:
                 self._insert_text(self.text_dox_results, f"• {cat.upper()}: {data}\\n")

"""

content = content.replace(old_cb, new_cb)

# We need to change where we run the background tasks, the 'category' arg was missing in the gui.py
old_task = """        if self.current_dox_username:
            self.orchestrator.submit_task(self.socmint_engine.run_all(self.current_dox_username))
        if self.current_dox_phone:
            self.orchestrator.submit_task(self.phone_engine.run_all(self.current_dox_phone))"""

new_task = """        if self.current_dox_username:
            self.orchestrator.submit_task("socmint", self.socmint_engine.run_all(self.current_dox_username))
        if self.current_dox_phone:
            self.orchestrator.submit_task("phone", self.phone_engine.run_all(self.current_dox_phone))"""

content = content.replace(old_task, new_task)

with open("sherlock_project/gui.py", "w") as f:
    f.write(content)
