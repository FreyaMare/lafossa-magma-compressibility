@echo off
rem ===========================================================================================
rem  Builds the Windows program "Magma Compressibility and Surface Uplift".
rem  Double-click this file (or run it in a Command Prompt). It needs Python 3.12, 3.13 or 3.14
rem  from python.org and an internet connection the first time (about 400 MB of packages).
rem  Results:  output\MagmaUplift_Setup_1.0.0.exe   (installer, if Inno Setup is available)
rem            output\MagmaUplift_portable.zip       (the same program without installation)
rem ===========================================================================================
setlocal
cd /d "%~dp0"
set "RC=0"
title Building Magma Compressibility and Surface Uplift
echo.
echo  === Magma Compressibility and Surface Uplift - Windows build ===
echo.

rem ---------------------------------------------------------------- 1. Python
set "PY="
py -3.13 -c "import sys" >nul 2>&1 && set "PY=py -3.13"
if not defined PY (py -3.12 -c "import sys" >nul 2>&1 && set "PY=py -3.12")
if not defined PY (py -3.14 -c "import sys" >nul 2>&1 && set "PY=py -3.14")
if not defined PY (python -c "import sys; sys.exit(0 if (3,12) <= sys.version_info[:2] <= (3,14) else 1)" >nul 2>&1 && set "PY=python")
if not defined PY goto nopython
echo [1/6] Python found: %PY%

rem ---------------------------------------------------------------- 2. packages
if not exist ".venv-build\Scripts\python.exe" (
    echo [2/6] Creating a private Python environment in .venv-build ...
    %PY% -m venv .venv-build || goto fail
)
set "VPY=%CD%\.venv-build\Scripts\python.exe"
echo [2/6] Installing the packages - the first time this downloads about 400 MB ...
"%VPY%" -m pip install --disable-pip-version-check --upgrade pip >nul
"%VPY%" -m pip install --disable-pip-version-check -r requirements.txt -c constraints.txt || goto fail

rem ---------------------------------------------------------------- 3. check the calculation
echo [3/6] Checking the calculation (thesis example) ...
"%VPY%" run_app.py --selftest "%CD%\selftest_source.txt" || goto testfail

rem ---------------------------------------------------------------- 4. build the program
echo [4/6] Building the program with PyInstaller - this takes a few minutes ...
"%VPY%" -m PyInstaller --noconfirm --clean MagmaUplift.spec || goto fail

echo [5/6] Checking the built program ...
start "" /wait "dist\MagmaUplift\MagmaUplift.exe" --selftest "%CD%\selftest_program.txt"
if errorlevel 1 goto testfail
type "selftest_program.txt"

rem ---------------------------------------------------------------- 6. installer and portable zip
if not exist output mkdir output
echo [6/6] Making the portable zip ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'dist\MagmaUplift' -DestinationPath 'output\MagmaUplift_portable.zip' -Force" || goto fail

call :findinno
if defined ISCC goto makeinstaller
echo.
if defined CI goto noinno
echo  The installer (setup.exe) is made with Inno Setup, a free tool that is not installed yet.
choice /c YN /m " Install Inno Setup now with winget"
if errorlevel 2 goto noinno
winget install --id JRSoftware.InnoSetup -e --accept-package-agreements --accept-source-agreements
call :findinno
if not defined ISCC goto noinno

:makeinstaller
echo [6/6] Making the installer with Inno Setup ...
"%ISCC%" /Qp installer.iss || goto fail
echo.
echo  ==========================================================================
echo   DONE.
echo   Installer:         %CD%\output\MagmaUplift_Setup_1.0.0.exe
echo   Portable version:  %CD%\output\MagmaUplift_portable.zip
echo   Program folder:    %CD%\dist\MagmaUplift\MagmaUplift.exe
echo  ==========================================================================
goto end

:noinno
echo.
echo  ==========================================================================
echo   DONE without installer (Inno Setup not available).
echo   Portable version:  %CD%\output\MagmaUplift_portable.zip
echo   Program folder:    %CD%\dist\MagmaUplift\MagmaUplift.exe
echo   To make the installer later: install Inno Setup 6 and run this file again.
echo  ==========================================================================
goto end

:findinno
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
exit /b 0

:nopython
echo.
echo  Python 3.12, 3.13 or 3.14 was not found.
echo  Install it from https://www.python.org/downloads/windows/ - tick "Add python.exe to PATH" -
echo  or run:   winget install -e --id Python.Python.3.13
echo  Then run this file again.
goto end

:testfail
set "RC=2"
echo.
echo  The check of the calculation FAILED. The details are in selftest_source.txt / selftest_program.txt.
goto end

:fail
set "RC=1"
echo.
echo  The build stopped with an error (see the messages above).

:end
echo.
if not defined CI pause
endlocal & exit /b %RC%
