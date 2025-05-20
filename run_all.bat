@echo off
REM --- run_benchmarks.bat ---
run_benchmarks.bat
REM 1) Parse GC logs
echo Running parse_gc_logs.py...
python "%~dp0scripts\parse_gc_logs.py"
if errorlevel 1 (
    echo [ERROR] parse_gc_logs.py failed with %errorlevel%.
    pause
    exit /b %errorlevel%
)

REM 2) Extract DaCapo results
echo Running extract_dacapo_results.py...
python "%~dp0scripts\extract_dacapo_results.py"
if errorlevel 1 (
    echo [ERROR] extract_dacapo_results.py failed with %errorlevel%.
    pause
    exit /b %errorlevel%
)

REM 3) Aggregate results
echo Running aggregate_results.py...
python "%~dp0scripts\aggregate_results.py"
if errorlevel 1 (
    echo [ERROR] aggregate_results.py failed with %errorlevel%.
    pause
    exit /b %errorlevel%
)

echo All is over..!
pause
