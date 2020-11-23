import os
import sys
import subprocess


def run_bot():
    interpreter = sys.executable
    auto_restart = True

    # This should never happen
    if interpreter is None:
        raise RuntimeError("Couldn't find Python's interpreter")

    cmd = (interpreter, "bot.py")

    while True:
        try:
            code = subprocess.call(cmd)
        except KeyboardInterrupt:
            code = 0
            break
        else:
            if code == 0:
                break
            elif code == 26:
                print("Restarting RoughSoul Bot...")
                continue
            else:
                if not auto_restart:
                    break

    print("RoughSoul Bot  has been terminated. Exit code: %d" % code)


run_bot()

