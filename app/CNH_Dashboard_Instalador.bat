@echo off
chcp 65001 >nul
title CNH Aftermarket Intelligence

cd /d "%~dp0"

echo.
echo ==========================================
echo   CNH AFTERMARKET INTELLIGENCE
echo ==========================================
echo.

:: --------------------------------------------------
:: Buscar Python
:: --------------------------------------------------

where py >nul 2>&1
if %errorlevel%==0 (
    set PY_CMD=py
    goto :python_found
)

where python >nul 2>&1
if %errorlevel%==0 (
    set PY_CMD=python
    goto :python_found
)

echo ERROR: Python no encontrado.
echo.
echo Instala Python desde:
echo https://www.python.org/downloads/
echo.
echo IMPORTANTE:
echo Marca "Add Python to PATH"
echo.
pause
exit /b 1

:python_found

echo [OK] Python encontrado

:: --------------------------------------------------
:: Crear entorno virtual
:: --------------------------------------------------

if not exist ".venv" (
    echo.
    echo [..] Creando entorno virtual...
    %PY_CMD% -m venv .venv

    if errorlevel 1 (
        echo ERROR creando entorno virtual
        pause
        exit /b 1
    )
)

echo [OK] Entorno virtual listo

:: --------------------------------------------------
:: Activar venv
:: --------------------------------------------------

call ".venv\Scripts\activate.bat"

:: --------------------------------------------------
:: Actualizar pip
:: --------------------------------------------------

echo.
echo [..] Actualizando pip...

python -m pip install --upgrade pip

if errorlevel 1 (
    echo ERROR actualizando pip
    pause
    exit /b 1
)

:: --------------------------------------------------
:: Instalar dependencias
:: --------------------------------------------------

echo.
echo [..] Instalando dependencias...


if errorlevel 1 (
    echo.
    echo ERROR instalando dependencias
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas

:: --------------------------------------------------
:: Verificar launcher
:: --------------------------------------------------

if not exist "app\launcher.py" (
    echo ERROR: No se encontro app\launcher.py
    pause
    exit /b 1
)

:: --------------------------------------------------
:: Crear lanzador dentro de app\
:: --------------------------------------------------

echo.
echo [..] Creando lanzador...

set VENV_PY=%~dp0.venv\Scripts\pythonw.exe
set LAUNCHER=%~dp0app\launcher.py
set WORKDIR=%~dp0app

echo @echo off                                                        > "app\Iniciar_Dashboard.bat"
echo chcp 65001 ^>nul                                                >> "app\Iniciar_Dashboard.bat"
echo cd /d "%WORKDIR%"                                               >> "app\Iniciar_Dashboard.bat"
echo start "" "%VENV_PY%" "%LAUNCHER%"                              >> "app\Iniciar_Dashboard.bat"
echo exit                                                            >> "app\Iniciar_Dashboard.bat"

if not exist "app\Iniciar_Dashboard.bat" (
    echo ERROR: No se pudo crear el lanzador
    pause
    exit /b 1
)

echo [OK] Lanzador creado

:: --------------------------------------------------
:: Crear acceso directo junto al instalador
:: --------------------------------------------------

echo.
echo [..] Creando acceso directo...

set PS_SCRIPT=$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%~dp0CNH Dashboard.lnk'); $Shortcut.TargetPath = '%~dp0app\Iniciar_Dashboard.bat'; $Shortcut.WorkingDirectory = '%~dp0app'; $Shortcut.IconLocation = '%~dp0app\cnh.ico'; $Shortcut.Save()

powershell -NoProfile -ExecutionPolicy Bypass -Command "%PS_SCRIPT%"

if not exist "%~dp0CNH Dashboard.lnk" (
    echo ERROR: No se pudo crear el acceso directo
    pause
    exit /b 1
)

echo [OK] Acceso directo creado

:: --------------------------------------------------
:: Ejecutar launcher
:: --------------------------------------------------

echo.
echo Iniciando launcher...
echo.

start "" "%~dp0app\Iniciar_Dashboard.bat"

exit