"""Floating sticky-notes window for Windows.

Opens the web app in a chromeless Edge window, keeps it on top at the right edge
of the screen, and grows/shrinks it when the page's title says [open]/[closed].
Run with pythonw (no console window). Uses only the Python standard library.
"""
import ctypes
import ctypes.wintypes as wt
import subprocess
import sys
import time

URL = "https://leecontract-crypto.github.io/sticky-notes/?float"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CLOSED_W, CLOSED_H = 230, 140      # collapsed window size (Edge enforces a minimum width)
STRIP_W = 44                       # how much of it peeks in from the screen edge
OPEN_W = 400                       # expanded: panel (340) + tab

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wt.UINT]
user32.SetWindowPos.restype = wt.BOOL
HWND_TOPMOST = wt.HWND(-1)
SWP_SHOWWINDOW = 0x0040
SPI_GETWORKAREA = 0x0030


def work_area():
    r = wt.RECT()
    user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(r), 0)
    return r.left, r.top, r.right, r.bottom


def find_window():
    found = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            n = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            if buf.value.startswith("Sticky Notes ["):
                found.append((hwnd, buf.value))
        return True

    user32.EnumWindows(cb, 0)
    return found[0] if found else (None, "")


def place(hwnd, is_open):
    """Expanded: full-height panel at the right edge. Collapsed: the window is parked
    mostly off the right-hand edge of the desktop so only the arrow strip shows
    (Edge won't make an app window narrower than ~222px, so we can't just shrink it)."""
    l, t, r, b = work_area()
    sc = (user32.GetDpiForWindow(hwnd) or 96) / 96   # sizes below are in CSS pixels
    open_w, strip_w = int(OPEN_W * sc), int(STRIP_W * sc)
    closed_w, closed_h = int(CLOSED_W * sc), int(CLOSED_H * sc)
    vright = user32.GetSystemMetrics(76) + user32.GetSystemMetrics(78)  # right edge of virtual desktop
    if is_open:
        user32.SetWindowPos(hwnd, HWND_TOPMOST, vright - open_w, t, open_w, b - t, SWP_SHOWWINDOW)
    else:
        y = t + (b - t - closed_h) // 2
        user32.SetWindowPos(hwnd, HWND_TOPMOST, vright - strip_w, y, closed_w, closed_h, SWP_SHOWWINDOW)


def main():
    subprocess.Popen([EDGE, f"--app={URL}"])
    last = None
    while True:
        hwnd, title = find_window()
        if hwnd is None:
            if last is not None:      # window was closed -> quit
                sys.exit(0)
        else:
            state = title.endswith("[open]")
            if state != last:
                place(hwnd, state)
                last = state
        time.sleep(0.25)


if __name__ == "__main__":
    main()
