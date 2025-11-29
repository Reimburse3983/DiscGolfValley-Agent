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
        time.sleep(5)
        self.find_window()

    def find_window(self):
        """Find the game window by executable name."""
        # First try: direct window title search
        hwnd = win32gui.FindWindowEx(None, None, None, "Disc Golf Valley")
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
            print(f"Warning: Could not focus window - {e}")
            # Continue anyway, might still work

    def get_window_rect(self):
        """Get window position and size."""
        if not self.hwnd:
            self.find_window()
        return win32gui.GetWindowRect(self.hwnd)

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
        """Navigate the game menu."""
        width, height, rect = self.get_size()
        print(f"Window: {width}x{height}, Rect: {rect}")
        
        self.click(700, 450)  # Click Play
        time.sleep(1)
        
        self.click(650, 200)  # Click Challenge the Valley
        time.sleep(1)

        self.click(675, 390)  # Click Play for Course
    
    def click_throw(self):
        self.click(425,435)
        time.sleep(1)

    def click_throw_debug(self, debug=True):
        """Click the throw button, with fresh coordinate recalculation each time.
        
        Parameters:
        - debug: if True, prints the screen coordinates to help diagnose drift.
        """
        # Ensure window is focused first (some games change layout when focused)
        if not self.hwnd:
            self.find_window()
        self.focus()

        # Recompute window/client info after focus
        try:
            hwnd = self.hwnd
            win_rect = win32gui.GetWindowRect(hwnd)
            client_rect = win32gui.GetClientRect(hwnd)
            client_left, client_top = win32gui.ClientToScreen(hwnd, (0, 0))
            throw_wx, throw_wy = 425, 435
            sx, sy = client_left + throw_wx, client_top + throw_wy
            cursor = win32api.GetCursorPos()

            if debug:
                print("--- click_throw_debug ---")
                print(f"hwnd={hwnd}")
                print(f"GetWindowRect: {win_rect}")
                print(f"GetClientRect: {client_rect}")
                print(f"ClientToScreen origin: ({client_left}, {client_top})")
                print(f"throw window-relative: ({throw_wx}, {throw_wy}) -> screen: ({sx}, {sy})")
                print(f"current cursor: {cursor}")

            pydirectinput.click(x=sx, y=sy)
            time.sleep(1)
        except Exception as e:
            print(f"click_throw_debug error: {e}")
            raise

    def click_throw_rel(self, relx: float, rely: float, debug=True):
        """Click at a position given as fractions of the client area.

        - `relx`, `rely` are in 0..1 (fraction of client width/height).
        This makes clicks robust to client resolution changes.
        """
        if not self.hwnd:
            self.find_window()
        self.focus()

        hwnd = self.hwnd
        # client rect gives width/height
        cl_left, cl_top = win32gui.ClientToScreen(hwnd, (0, 0))
        client_rect = win32gui.GetClientRect(hwnd)
        client_w = client_rect[2]
        client_h = client_rect[3]

        # clamp
        rx = max(0.0, min(1.0, float(relx)))
        ry = max(0.0, min(1.0, float(rely)))

        wx = int(rx * client_w)
        wy = int(ry * client_h)
        sx = cl_left + wx
        sy = cl_top + wy

        if debug:
            print(f"click_throw_rel: client_size=({client_w},{client_h}), rel=({rx},{ry}), window-relative=({wx},{wy}), screen=({sx},{sy})")

        pydirectinput.click(x=sx, y=sy)
        time.sleep(1)

    def take_screenshot(self, top_left, bottom_right, save_path=None, relative=True, rel_norm=False, clip_to_client=True):
        """Take a screenshot of a region inside the game window.

        Parameters:
        - top_left: (x, y) tuple of top-left corner. If `relative` it's window-client relative.
                    When `rel_norm=True` the values must be normalized floats in 0..1.
        - bottom_right: (x, y) tuple of bottom-right corner. Same semantics as `top_left`.
        - save_path: optional path to save the captured image (PNG/JPEG).
        - relative: whether provided coordinates are relative to the game window client origin
                    (default True). If False, coordinates are treated as absolute screen coords.
        - rel_norm: when True and `relative` is True, treat the provided coords as normalized
                    fractions of the client area (0..1). This keeps crops resolution-independent.

        Returns: a Pillow `Image` instance with the captured region.
        """
        try:
            import mss
            from PIL import Image
        except Exception as e:
            raise RuntimeError("mss and Pillow are required for screenshots. Install with `pip install mss pillow`") from e

        if not self.hwnd:
            self.find_window()

        if relative:
            # Get client origin and size
            client_left, client_top = win32gui.ClientToScreen(self.hwnd, (0, 0))
            client_rect = win32gui.GetClientRect(self.hwnd)
            client_w = client_rect[2]
            client_h = client_rect[3]

            if rel_norm:
                # top_left/bottom_right are normalized fractions in 0..1
                nl, nt = float(top_left[0]), float(top_left[1])
                nr, nb = float(bottom_right[0]), float(bottom_right[1])
                # clamp
                nl = max(0.0, min(1.0, nl))
                nt = max(0.0, min(1.0, nt))
                nr = max(0.0, min(1.0, nr))
                nb = max(0.0, min(1.0, nb))
                left = client_left + int(nl * client_w)
                top = client_top + int(nt * client_h)
                right = client_left + int(nr * client_w)
                bottom = client_top + int(nb * client_h)
            else:
                # Convert from window-relative pixels to absolute screen coords
                left = client_left + int(top_left[0])
                top = client_top + int(top_left[1])
                right = client_left + int(bottom_right[0])
                bottom = client_top + int(bottom_right[1])
        else:
            left, top = int(top_left[0]), int(top_left[1])
            right, bottom = int(bottom_right[0]), int(bottom_right[1])

        # Optionally clip the region to the client area to avoid off-screen or window-decor captures
        if clip_to_client and relative:
            # client_left/client_top and client_w/client_h already available
            client_left, client_top = win32gui.ClientToScreen(self.hwnd, (0, 0))
            client_rect = win32gui.GetClientRect(self.hwnd)
            client_w = client_rect[2]
            client_h = client_rect[3]
            client_right = client_left + client_w
            client_bottom = client_top + client_h

            orig = (left, top, right, bottom)
            left = max(left, client_left)
            top = max(top, client_top)
            right = min(right, client_right)
            bottom = min(bottom, client_bottom)
            if (left, top, right, bottom) != orig:
                print(f"take_screenshot: clipped region {orig} -> {(left, top, right, bottom)} to client bounds")

        width = right - left
        height = bottom - top
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid region dimensions for screenshot after clipping: {(left,top,right,bottom)}")

        with mss.mss() as sct:
            rect = {"left": left, "top": top, "width": width, "height": height}
            sct_img = sct.grab(rect)
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            if save_path:
                img.save(save_path)
            return img

    def take_screenshot_norm(self, top_left_norm, bottom_right_norm, save_path=None):
        """Convenience wrapper: take a screenshot using normalized 0..1 coordinates.

        - `top_left_norm` and `bottom_right_norm` are (x,y) tuples with values in 0..1
          relative to the client area (0,0 top-left, 1,1 bottom-right).
        """
        return self.take_screenshot(top_left_norm, bottom_right_norm, save_path=save_path,
                                    relative=True, rel_norm=True)

