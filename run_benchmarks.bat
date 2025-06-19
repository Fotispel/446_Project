@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

SET "JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-21.0.7.6-hotspot"
SET JAVA_CMD=%JAVA_HOME%\bin\java.exe

SET "DACAPO_JAR=.\dacapo-23.11-MR2-chopin.jar"

SET "GC_LOG_DIR=.\gc_logs"
SET "DACAPO_OUT_DIR=.\dacapo_outputs"
SET "RESULTS_DIR=.\results"
MKDIR %GC_LOG_DIR% 2>NUL
MKDIR %DACAPO_OUT_DIR% 2>NUL
MKDIR %RESULTS_DIR% 2>NUL

SET GCS_TO_TEST=G1 Parallel Shenandoah ZGC
SET HEAP_SIZES_TO_TEST=2g 12g
SET BENCHMARKS_TO_TEST=avrora lusearch tomcat

FOR %%G IN (%GCS_TO_TEST%) DO (
    FOR %%H IN (%HEAP_SIZES_TO_TEST%) DO (
        FOR %%B IN (%BENCHMARKS_TO_TEST%) DO (
            ECHO Running GC: %%G, Heap: %%H, Benchmark: %%B
            SET "GC_OPTS="
            IF "%%G"=="G1" ( SET "GC_OPTS=-XX:+UseG1GC" )
            IF "%%G"=="Parallel" ( SET "GC_OPTS=-XX:+UseParallelGC" )
            IF "%%G"=="ZGC" ( SET "GC_OPTS=-XX:+UseZGC" )
            IF "%%G"=="Shenandoah" ( SET "GC_OPTS=-XX:+UseShenandoahGC" )
            SET "HEAP_OPTS=-Xms%%H -Xmx%%H"
            SET "LOG_FILE_GC_PATH=!GC_LOG_DIR!\gc_%%G_%%H_%%B.log"
            SET "LOG_FILE_DACAPO_PATH=!DACAPO_OUT_DIR!\dacapo_%%G_%%H_%%B.log"
            SET "GC_LOG_JVM_OPTS=-Xlog:gc=debug,gc+heap=debug,gc+phases=debug,safepoint=debug:file=!LOG_FILE_GC_PATH!:time,level,tags,pid,tid"
            ECHO Command being executed...
            !JAVA_CMD! !GC_OPTS! !HEAP_OPTS! !GC_LOG_JVM_OPTS! --data-set-location . -jar !DACAPO_JAR! %%B -n 3 > "!LOG_FILE_DACAPO_PATH!" 2>&1
            "!JAVA_CMD!" !GC_OPTS! !HEAP_OPTS! !GC_LOG_JVM_OPTS! -jar !DACAPO_JAR! %%B -n 3 > "!LOG_FILE_DACAPO_PATH!" 2>&1
            FOR /F "tokens=1-2 delims=," %%a IN ('echo !TIME!') DO SET CURRENT_TIME=%%a
            ECHO Completed GC: %%G, Heap: %%H, Benchmark: %%B at: %DATE% !CURRENT_TIME!
            ECHO -----------------------------------------------------
        )
    )
)
ECHO All benchmarks finished.

ECHO.
ECHO === Finished at: %DATE% %TIME% ===

ENDLOCAL