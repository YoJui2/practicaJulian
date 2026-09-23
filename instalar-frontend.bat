@echo off
setlocal
cd /d "%~dp0"

set "PATH=C:\Program Files\nodejs;%PATH%"
call npm --prefix frontend install
if errorlevel 1 goto error

echo.
echo Frontend instalado correctamente.
exit /b 0

:error
echo.
echo No se pudo instalar el frontend. Revisa la salida de npm.
exit /b 1
