@echo off
echo ========================================
echo   Starting Stagehand Browser Server
echo ========================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed!
    echo Please install from: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if in correct directory
if not exist "package.json" (
    echo ERROR: package.json not found!
    echo Please run this script from the browser-server directory
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating from .env.example...
    copy .env.example .env
    echo.
    echo Please edit .env and add your GEMINI_API_KEY
    echo Then run this script again.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: npm install failed!
        pause
        exit /b 1
    )
    echo.
)

echo Starting server...
echo.
echo Keep this window open while using the browser!
echo Press Ctrl+C to stop the server.
echo.

call npm start
