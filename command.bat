@echo off
set /p input="enter command/benchmark: "
echo Input: %input%
java -jar dacapo-23.11-MR2-chopin.jar %input%
pause