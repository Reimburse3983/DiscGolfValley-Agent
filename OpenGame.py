import win32process
import win32api
import win32con
import time
import os

GAME_EXE_NAME = "DiscGolf.exe"
STEAM_APP_ID = "1642890"


def is_game_running():
    pids = win32process.EnumProcesses()
    for pid in pids:
        try:
            h = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
            exe = win32process.GetModuleFileNameEx(h, 0)
            win32api.CloseHandle(h)
            if GAME_EXE_NAME.lower() in exe.lower():
                return True
        except:
            pass
    return False


def launch_game():
    print("Game not running. Starting ...")
    os.system(f"start steam://rungameid/{STEAM_APP_ID}")
    

def ensure_game_running(timeout=30):
    if not is_game_running():
        launch_game()

    start = time.time()
    while time.time() - start < timeout:
        if is_game_running():
            print("Game running.")
            return True
        time.sleep(0.5)

    raise TimeoutError("Game didn't start.")


if __name__ == "__main__":
    ensure_game_running()
