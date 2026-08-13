"""
UI Orchestrator
Bridges the gap between async reconnaissance engines and the synchronous Tkinter main loop.
"""

import asyncio
import threading
import queue

class UIOrchestrator:
    def __init__(self, gui_callback_msg, gui_callback_progress, gui_callback_result):
        """
        Initializes the orchestrator.
        :param gui_callback_msg: Function to call to print text to GUI.
        :param gui_callback_progress: Function to call to update progress bar.
        :param gui_callback_result: Function to call to add a result to the filter panel.
        """
        self.message_queue = queue.Queue()
        self.gui_callback_msg = gui_callback_msg
        self.gui_callback_progress = gui_callback_progress
        self.gui_callback_result = gui_callback_result

        self.loop = asyncio.new_event_loop()
        self.worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.worker_thread.start()

        # Start checking the queue from the main thread
        self.is_running = True

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def submit_task(self, category: str, coro):
        """
        Submit an async task to the background event loop.
        Wraps the coroutine to capture its result and post it back to the UI.
        """
        async def _wrapper():
            try:
                result = await coro
                # Check if it's a list of results or a single dict
                if isinstance(result, list):
                    for r in result:
                         self.post_result(category, r)
                else:
                    self.post_result(category, result)
            except Exception as e:
                self.post_message(f"Error in async task {category}: {e}")

        asyncio.run_coroutine_threadsafe(_wrapper(), self.loop)

    def post_message(self, text):
        self.message_queue.put({"type": "msg", "data": text})

    def post_progress(self, current, total):
         self.message_queue.put({"type": "progress", "current": current, "total": total})

    def post_result(self, category, data):
        """Posts a structured result for the filter panel."""
        self.message_queue.put({"type": "result", "category": category, "data": data})

    def process_queue_sync(self, root):
        """
        This needs to be called via Tkinter's `after` method.
        It pulls items from the thread-safe queue and updates the UI.
        """
        if not self.is_running:
            return

        try:
            while True:
                item = self.message_queue.get_nowait()
                if item["type"] == "msg":
                    self.gui_callback_msg(item["data"])
                elif item["type"] == "progress":
                    self.gui_callback_progress(item["current"], item["total"])
                elif item["type"] == "result":
                    self.gui_callback_result(item["category"], item["data"])
                self.message_queue.task_done()
        except queue.Empty:
            pass
        finally:
            # Reschedule itself
            root.after(100, self.process_queue_sync, root)

    def stop(self):
        self.is_running = False
        self.loop.call_soon_threadsafe(self.loop.stop)
