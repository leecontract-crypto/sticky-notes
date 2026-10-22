@echo off
rem Double-click to start the floating sticky notes. Needs only Windows + Microsoft Edge (no Python).
start "" powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0float.ps1"
