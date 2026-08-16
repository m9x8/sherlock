import sys
import asyncio
import threading
import concurrent.futures

def setup_windows_event_loop():
    """Sets the correct event loop policy for Windows to support subprocesses (like Playwright)."""
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def run_async_safely(coro):
    """
    Safely runs a coroutine in a thread-safe manner, establishing a new event loop if necessary.
    Handles the Windows event loop policy correctly.
    """
    setup_windows_event_loop()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We are already in an event loop (e.g. called from another async function but shouldn't be using this)
        # Or we are in a thread where an event loop is running. Submit to an executor.
        with concurrent.futures.ThreadPoolExecutor(1) as pool:
            def _run():
                setup_windows_event_loop()
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
            return pool.submit(_run).result()
    else:
        # No event loop running, we can just use asyncio.run but we must make sure the policy is set
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()
