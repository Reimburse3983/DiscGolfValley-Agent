"""
pick_coords.py

Simple GUI to capture pixel coordinates relative to a chosen window.

How to use:
1. Run the script: `python pick_coords.py`
2. Make your game window active (click it), then click "Set Window" in this tool.
3. Move the mouse pointer over the game object you want the coordinates for.
4. Click "Record" to add the current window-relative coords to the list.
5. Click "Save" to write recorded coords to a file (default `coords.txt`).

This script uses only the standard library plus `pywin32` (which your repo already uses).
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import win32gui
import win32api
import time

class CoordPicker:
    def __init__(self, master):
        self.master = master
        master.title('Pick coordinates (window-relative)')

        self.hwnd = None
        self.client_origin = (0, 0)
        self.records = []

        # UI
        self.info_label = tk.Label(master, text='Window: <not set>')
        self.info_label.pack(padx=8, pady=(8, 2))

        self.coord_label = tk.Label(master, text='Cursor (screen): -, -\nRelative: -, -', font=('Consolas', 12))
        self.coord_label.pack(padx=8, pady=4)

        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=6)

        self.set_btn = tk.Button(btn_frame, text='Set Now (uses current foreground)', command=self.set_window)
        self.set_btn.grid(row=0, column=0, padx=4, pady=4)

        # delayed set controls
        self.delay_var = tk.IntVar(value=3)
        self.delay_spin = tk.Spinbox(btn_frame, from_=1, to=10, width=3, textvariable=self.delay_var)
        self.delay_spin.grid(row=0, column=1, padx=(6, 2))
        self.set_after_btn = tk.Button(btn_frame, text='Set After (s)', command=self.set_window_delayed)
        self.set_after_btn.grid(row=0, column=2, padx=4)

        self.record_btn = tk.Button(btn_frame, text='Record', command=self.record_coord)
        self.record_btn.grid(row=0, column=1, padx=4)

        self.clear_btn = tk.Button(btn_frame, text='Clear', command=self.clear_records)
        self.clear_btn.grid(row=0, column=2, padx=4)

        self.save_btn = tk.Button(btn_frame, text='Save', command=self.save_records)
        self.save_btn.grid(row=0, column=3, padx=4)

        self.quit_btn = tk.Button(btn_frame, text='Quit', command=master.quit)
        self.quit_btn.grid(row=0, column=4, padx=4)

        self.listbox = tk.Listbox(master, width=48, height=8)
        self.listbox.pack(padx=8, pady=(6, 12))

        # Start updating
        self.update_loop()

    def set_window(self):
        """Capture the current foreground window immediately."""
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            messagebox.showerror('Error', 'No foreground window detected')
            return
        try:
            title = win32gui.GetWindowText(hwnd)
        except Exception:
            title = '<unknown>'
        self.hwnd = hwnd
        client_left, client_top = win32gui.ClientToScreen(hwnd, (0, 0))
        self.client_origin = (client_left, client_top)
        self.info_label.config(text=f'Window: {title} (hwnd={hwnd})\nClient origin: {self.client_origin}')

    def set_window_delayed(self):
        """Start a countdown then capture whichever window is foreground."""
        try:
            delay = int(self.delay_var.get())
        except Exception:
            delay = 3

        self.info_label.config(text=f'Waiting {delay}s to capture foreground window...')
        self.master.after(100, lambda: self._delayed_countdown(delay))

    def _delayed_countdown(self, remaining):
        if remaining <= 0:
            # capture foreground
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                messagebox.showerror('Error', 'No foreground window detected after countdown')
                self.info_label.config(text='Window: <not set>')
                return
            try:
                title = win32gui.GetWindowText(hwnd)
            except Exception:
                title = '<unknown>'
            self.hwnd = hwnd
            client_left, client_top = win32gui.ClientToScreen(hwnd, (0, 0))
            self.client_origin = (client_left, client_top)
            self.info_label.config(text=f'Window: {title} (hwnd={hwnd})\nClient origin: {self.client_origin}')
            return

        # update label with remaining seconds and schedule next tick
        self.info_label.config(text=f'Waiting {remaining}s to capture foreground window...')
        self.master.after(1000, lambda: self._delayed_countdown(remaining - 1))

    def get_cursor_positions(self):
        sx, sy = win32api.GetCursorPos()
        if self.hwnd:
            clx, cly = self.client_origin
            relx = sx - clx
            rely = sy - cly
            return (sx, sy), (relx, rely)
        else:
            return (sx, sy), (None, None)

    def update_loop(self):
        (sx, sy), (relx, rely) = self.get_cursor_positions()
        if relx is None:
            rel_text = 'relative: <window not set>'
        else:
            rel_text = f'relative: {relx}, {rely}'
        self.coord_label.config(text=f'Cursor (screen): {sx}, {sy}\n{rel_text}')
        # schedule next update
        self.master.after(80, self.update_loop)

    def record_coord(self):
        (sx, sy), (relx, rely) = self.get_cursor_positions()
        if relx is None:
            messagebox.showwarning('Window not set', 'Set the window first (make game active and press "Set Window").')
            return
        entry = (int(relx), int(rely))
        self.records.append(entry)
        self.listbox.insert(tk.END, f'{entry[0]}, {entry[1]}')

    def clear_records(self):
        self.records.clear()
        self.listbox.delete(0, tk.END)

    def save_records(self):
        if not self.records:
            messagebox.showinfo('No data', 'No recorded coordinates to save')
            return
        file_path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt')], initialfile='coords.txt')
        if not file_path:
            return
        try:
            with open(file_path, 'w') as f:
                for x, y in self.records:
                    f.write(f'{x},{y}\n')
            messagebox.showinfo('Saved', f'Saved {len(self.records)} coords to {file_path}')
        except Exception as e:
            messagebox.showerror('Error saving', str(e))


if __name__ == '__main__':
    root = tk.Tk()
    app = CoordPicker(root)
    root.mainloop()
