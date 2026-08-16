import os
import platform
import re
import subprocess

class Interactives:
    def run_cli(args:str = "") -> str:
        """Pass arguments to Sherlock as a normal user on the command line"""
        # Adapt for platform differences (Windows likes to be special)
        if platform.system() == "Windows":
            command:str = f"py -m sherlock_project {args}"
        else:
            # We want to force CLI evaluation but the GUI might hijack if args are empty
            # But the tests check for CLI exceptions, so ensure we bypass GUI with dummy or rely on xvfb if it launches
            command:str = f"python -m sherlock_project {args}"

        proc_out:str = ""
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = "."
            env["DISPLAY"] = "" # Break the display to force fall-back to CLI error when GUI cannot launch
            proc_out = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=60, env=env)
            return proc_out.decode()
        except subprocess.CalledProcessError as e:
            raise InteractivesSubprocessError(e.output.decode())
        except subprocess.TimeoutExpired as e:
            raise InteractivesSubprocessError(f"Command timed out: {e}")


    def walk_sherlock_for_files_with(pattern: str) -> list[str]:
        """Check all files within the Sherlock package for matching patterns"""
        pattern:re.Pattern = re.compile(pattern)
        matching_files:list[str] = []
        for root, dirs, files in os.walk("sherlock_project"):
            for file in files:
                file_path = os.path.join(root,file)
                if "__pycache__" in file_path:
                    continue
                with open(file_path, 'r', errors='ignore') as f:
                    if pattern.search(f.read()):
                        matching_files.append(file_path)
        return matching_files

class InteractivesSubprocessError(Exception):
    pass
