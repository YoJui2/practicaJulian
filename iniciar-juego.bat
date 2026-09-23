@echo off
setlocal
cd /d "%~dp0"

docker compose up -d db
if errorlevel 1 goto database_error

if not exist "frontend\node_modules" (
    call "%~dp0instalar-frontend.bat"
    if errorlevel 1 exit /b 1
)

start "API de preguntas" /D "%~dp0" cmd /k poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

set "PATH=C:\Program Files\nodejs;%PATH%"
echo.
echo Iniciando el juego en http://localhost:5173
echo La API se abrira en otra ventana en http://localhost:8000
echo Presiona Ctrl+C para detener el frontend.
echo.
call npm --prefix frontend run dev
exit /b %errorlevel%

:database_error
echo.
echo No se pudo iniciar PostgreSQL. Verifica que Docker Desktop este abierto.
exit /b 1
