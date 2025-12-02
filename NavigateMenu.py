import win32gui
import win32process
import win32con
import win32api
import pydirectinput
import time
from PIL import ImageGrab
import pyautogui
import pygetwindow as gw
pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False


class GameWindow:
    def __init__(self, exe_name):
        self.exe_name = exe_name
        self.hwnd = None
        time.sleep(20)
        self.find_window()

    def find_window(self):
        """Find the game window by executable name."""
        # First try: direct window title search
        hwnd = win32gui.FindWindowEx(None, None, None, "DiscGolf")
        if hwnd:
            self.hwnd = hwnd
            return hwnd

        # Second try: search by executable process
        def callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                hproc = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                    False, pid
                )
                exe_path = win32process.GetModuleFileNameEx(hproc, 0)
                win32api.CloseHandle(hproc)
                if self.exe_name.lower() in exe_path.lower():
                    self.hwnd = hwnd
            except:
                pass

        win32gui.EnumWindows(callback, None)
        if not self.hwnd:
            raise Exception(f"Window not found for: {self.exe_name}")
        return self.hwnd

    def focus(self):
        """Bring window to foreground."""
        if not self.hwnd:
            self.find_window()
        
        try:
            # Restore if minimized
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            time.sleep(0.05)
            
            # Set to foreground
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.05)
            
            # Activate the window
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
            time.sleep(0.05)
        except Exception as e:
            print(f"Tring fallback for focus window - {e}")
            # Fallback: try clicking the window center to force focus
            try:
                lefttop, rightbottom = win32gui.ClientToScreen(self.hwnd, (0, 0))
                cx = lefttop+1
                cy = rightbottom+1
                pyautogui.click(cx, cy)
                time.sleep(1)
            except Exception as e2:
                print(f"Warning: fallback focus click failed - {e2}")

    def get_window_rect(self):
        """Get window position and size."""
        if not self.hwnd:
            self.find_window()
        return win32gui.GetClientRect(self.hwnd)

    def get_size(self):
        """Get window width and height."""
        left, top, right, bottom = self.get_window_rect()
        return right - left, bottom - top, (left, top, right, bottom)

    def to_screen_coords(self, wx, wy):
        """Convert window-relative coords to screen coords."""
        client_left, client_top = win32gui.ClientToScreen(self.hwnd, (0, 0))
        return client_left + wx, client_top + wy

    def click(self, wx, wy):
        """Click at window-relative coordinates."""
        self.focus()
        sx, sy = self.to_screen_coords(wx, wy)
        pydirectinput.click(x=sx, y=sy)
        time.sleep(0.1)

    def move(self, wx, wy):
        """Move mouse to window-relative coordinates."""
        self.focus()
        sx, sy = self.to_screen_coords(wx, wy)
        pydirectinput.moveTo(sx, sy)

    def press_key(self, key):
        """Press a keyboard key."""
        self.focus()
        pydirectinput.press(key)

    def drag(self, from_wx, from_wy, to_wx, to_wy, duration=0.2):
        """Drag from one window-relative position to another."""
        self.focus()
        x1, y1 = self.to_screen_coords(from_wx, from_wy)
        x2, y2 = self.to_screen_coords(to_wx, to_wy)
        pydirectinput.moveTo(x1, y1)
        pydirectinput.mouseDown()
        pydirectinput.moveTo(x2, y2, duration=duration)
        pydirectinput.mouseUp()

    def navigate_menu(self):
        self.focus()
        """Navigate the game menu."""
        width, height, rect = self.get_size()
        print(f"Window: {width}x{height}, Rect: {rect}")
        
        self.click(1200, 650)  # Click Play
        time.sleep(1)
        
        self.click(800, 270)  # Click Challenge the Valley
        time.sleep(1)

        self.click(1000, 600)  # Click Play for Course
    
    def click_throw(self):
        self.click(640, 650)
        time.sleep(1)

    