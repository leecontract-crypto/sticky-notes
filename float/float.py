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
CLOSED_W, CLOSED_H = 44, 140       # collapsed: just the arrow tab
OPEN_W = 390                       # expanded: panel (340) + tab

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
HWND_TOPMOST = -1
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
    l, t, r, b = work_area()
    if is_open:
        w, h, y = OPEN_W, b - t, t
    else:
        w, h, y = CLOSED_W, CLOSED_H, t + (b - t - CLOSED_H) // 2
    user32.SetWindowPos(hwnd, HWND_TOPMOST, r - w, y, w, h, SWP_SHOWWINDOW)


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
