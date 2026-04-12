@echo off
set PYTHON=C:\Users\emman\AppData\Local\Python\bin\python.exe
set PROJECT=C:\Users\emman\OneDrive\Documents\canada-job-market-intelligence
set LOG=%PROJECT%\run_log.txt

cd /d "%PROJECT%"

echo [%date% %time%] Starting pipeline run >> "%LOG%"

echo Running adzuna_test.py...
"%PYTHON%" "%PROJECT%\adzuna_test.py"
if %errorlevel% neq 0 (
    echo [%date% %time%] ERROR: adzuna_test.py failed >> "%LOG%"
    exit /b 1
)

echo Running clean_jobs.py...
"%PYTHON%" "%PROJECT%\clean_jobs.py"
if %errorlevel% neq 0 (
    echo [%date% %time%] ERROR: clean_jobs.py failed >> "%LOG%"
    exit /b 1
)

echo Running update_latest.py...
"%PYTHON%" "%PROJECT%\update_latest.py"
if %errorlevel% neq 0 (
    echo [%date% %time%] ERROR: update_latest.py failed >> "%LOG%"
    exit /b 1
)

echo [%date% %time%] Pipeline completed successfully >> "%LOG%"
echo Done.
