import win32gui
import win32process
import win32con
import win32api
import pydirectinput
import time

pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False


class GameWindow:
    def __init__(self, exe_name):
        self.exe_name = exe_name
        self.hwnd = None

 
    def find_window(self):
        hwnd_list = []

        def callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return

            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                hproc = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                    False,
                    pid
                )
                exe_path = win32process.GetModuleFileNameEx(hproc, 0)
                win32api.CloseHandle(hproc)

                if self.exe_name.lower() in exe_path.lower():
                    hwnd_list.append(hwnd)

            except:
                pass

        win32gui.EnumWindows(callback, None)
        self.hwnd = hwnd_list[0] if hwnd_list else None
        return self.hwnd

    def get_size(self):
        if not self.hwnd:
            if not self.find_window():
                raise Exception("Window not found")

        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        width = right - left
        height = bottom - top

        return width, height, (left, top, right, bottom)

    def focus(self):
        if not self.hwnd:
            if not self.find_window():
                raise Exception("Window not found")

        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetWindowPos(
            self.hwnd, win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
        win32gui.SetWindowPos(
            self.hwnd, win32con.HWND_NOTOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
        win32gui.SetForegroundWindow(self.hwnd)
        time.sleep(0.05)

    
    def to_screen(self, wx, wy):
    # Get the client area origin (actual game surface)
        client_left, client_top = win32gui.ClientToScreen(self.hwnd, (0, 0))
        return client_left + wx, client_top + wy


    def click(self, wx, wy):
        self.focus()

        # Get client area (game surface)
        cl_left, cl_top = win32gui.ClientToScreen(self.hwnd, (0, 0))
        cl_right, cl_bottom = win32gui.ClientToScreen(
            self.hwnd,
            win32gui.GetClientRect(self.hwnd)[2:]
        )

        # Compute actual screen coords
        sx, sy = self.to_screen(wx, wy)

        # ---- SAFETY CHECK ----
        if not (cl_left <= sx <= cl_right and cl_top <= sy <= cl_bottom):
            print("Blocked click outside game window:", (sx, sy))
            return  # do not click

        # Safe to click
        pydirectinput.click(x=sx, y=sy)


    def move(self, wx, wy):
        self.focus()
        x, y = self.to_screen(wx, wy)
        pydirectinput.moveTo(x, y)

    def press_key(self, key):
        self.focus()
        pydirectinput.press(key)

    def drag(self, from_wx, from_wy, to_wx, to_wy, duration=0.2):
        self.focus()
        x1, y1 = self.to_screen(from_wx, from_wy)
        x2, y2 = self.to_screen(to_wx, to_wy)

        pydirectinput.moveTo(x1, y1)
        pydirectinput.mouseDown()
        pydirectinput.moveTo(x2, y2, duration=duration)
        pydirectinput.mouseUp()


game = GameWindow("DiscGolf.exe")

width, height, rect = game.get_size()

print("Width:", width)
print("Height:", height)
print("Rect:", rect)

game.focus()

#Click Play
game.click(700,450)
time.sleep(1)

#Click Challenge the Valley
game.click(650,200)
time.sleep(1)
