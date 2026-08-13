import re

with open("sherlock_project/gui.py", "r") as f:
    content = f.read()

old_cb = """    def _orchestrator_msg_callback(self, text):
        # We can route this to the active tab if desired, or print it.
        # This demonstrates receiving async events safely.
        print(f"[Orchestrator]: {text}")"""

new_cb = """    def _orchestrator_msg_callback(self, text):
        if hasattr(self, 'text_dox_results'):
            self._insert_text(self.text_dox_results, f"{text}\\n")"""

content = content.replace(old_cb, new_cb)

with open("sherlock_project/gui.py", "w") as f:
    f.write(content)
