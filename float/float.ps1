# Floating sticky-notes window for Windows (PowerShell version of float.py; needs no install).
# Opens the web app in a chromeless Edge window, keeps it on top at the right edge of the
# screen, and grows/shrinks it when the page's title says [open]/[closed].

$Url     = 'https://leecontract-crypto.github.io/sticky-notes/?float'
$ClosedW = 230; $ClosedH = 140   # collapsed window size (Edge enforces a minimum width)
$StripW  = 44                    # how much of it peeks in from the screen edge
$OpenW   = 400                   # expanded: panel (340) + tab

$edge = @(
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { $edge = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe' -ErrorAction SilentlyContinue).'(default)' }
if (-not $edge) { exit 1 }

Add-Type @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class Win {
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p, IntPtr l);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int w, int cx, uint f);
    [DllImport("user32.dll")] public static extern bool SystemParametersInfo(uint a, uint b, ref RECT r, uint c);
    [DllImport("user32.dll")] public static extern int GetSystemMetrics(int i);
    [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
    public static IntPtr Find(out string title) {
        IntPtr found = IntPtr.Zero; string t = "";
        EnumWindows((h, l) => {
            if (found == IntPtr.Zero && IsWindowVisible(h)) {
                var sb = new StringBuilder(256); GetWindowText(h, sb, 256);
                if (sb.ToString().StartsWith("Sticky Notes [")) { found = h; t = sb.ToString(); }
            }
            return true;
        }, IntPtr.Zero);
        title = t; return found;
    }
}
'@
[Win]::SetProcessDPIAware() | Out-Null

function Place($h, $isOpen) {
    $r = New-Object Win+RECT
    [Win]::SystemParametersInfo(0x30, 0, [ref]$r, 0) | Out-Null     # work area
    $dpi = [Win]::GetDpiForWindow($h); if ($dpi -eq 0) { $dpi = 96 }
    $sc = $dpi / 96
    $vright = [Win]::GetSystemMetrics(76) + [Win]::GetSystemMetrics(78)   # right edge of virtual desktop
    $top = [IntPtr](-1)                                                   # HWND_TOPMOST
    if ($isOpen) {
        $w = [int]($OpenW * $sc)
        [Win]::SetWindowPos($h, $top, $vright - $w, $r.T, $w, $r.B - $r.T, 0x40) | Out-Null
    } else {
        $ch = [int]($ClosedH * $sc)
        $y = $r.T + [int](($r.B - $r.T - $ch) / 2)
        [Win]::SetWindowPos($h, $top, $vright - [int]($StripW * $sc), $y, [int]($ClosedW * $sc), $ch, 0x40) | Out-Null
    }
}

Start-Process $edge "--app=$Url"
$last = $null
while ($true) {
    $title = ''
    $h = [Win]::Find([ref]$title)
    if ($h -eq [IntPtr]::Zero) {
        if ($null -ne $last) { exit 0 }          # window was closed -> quit
    } else {
        $state = $title.EndsWith('[open]')
        if ($state -ne $last) { Place $h $state; $last = $state }
    }
    Start-Sleep -Milliseconds 250
}
