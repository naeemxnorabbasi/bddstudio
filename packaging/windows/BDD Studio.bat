@echo off
setlocal

cd /d "%~dp0"

set BDDSTUDIO_PORTABLE_HOME=%CD%

if exist "%CD%\graphviz\bin\dot.exe" (
  set BDDSTUDIO_DOT=%CD%\graphviz\bin\dot.exe
  set PATH=%CD%\graphviz\bin;%PATH%
)

start "" http://127.0.0.1:8765

if exist "%CD%\bddstudio.exe" (
  "%CD%\bddstudio.exe" serve --host 127.0.0.1 --port 8765 --no-browser
) else if exist "%CD%\bddstudio\bddstudio.exe" (
  "%CD%\bddstudio\bddstudio.exe" serve --host 127.0.0.1 --port 8765 --no-browser
) else (
  echo Could not find BDD Studio executable.
  echo Expected bddstudio.exe or bddstudio\bddstudio.exe.
  pause
  exit /b 1
)

pause
