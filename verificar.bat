@echo off
setlocal
cd /d "%~dp0"
set "PATH=C:\Program Files\nodejs;%PATH%"

call npm --prefix frontend run quality
if errorlevel 1 goto frontend_error

call npm --prefix frontend run build
if errorlevel 1 goto frontend_error

call poetry run pytest
if errorlevel 1 goto api_error

echo.
echo Verificacion completa: frontend y API pasaron las pruebas.
exit /b 0

:frontend_error
echo.
echo Fallo la verificacion del frontend.
exit /b 1

:api_error
echo.
echo Fallaron las pruebas de la API.
exit /b 1
