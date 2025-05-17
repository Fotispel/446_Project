@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM --- Ρυθμίσεις ---
REM Αντικαταστήστε με τη διαδρομή του JDK σας (JDK 17+ συνιστάται για ZGC/Shenandoah)
SET "JAVA_HOME=C:\Program Files\Java\jdk-21"
SET JAVA_CMD=%JAVA_HOME%\bin\java.exe

REM Αντικαταστήστε με το όνομα του DaCapo JAR σας
SET "DACAPO_JAR=.\dacapo-23.11-MR2-chopin.jar"

SET "GC_LOG_DIR=.\gc_logs"
SET "DACAPO_OUT_DIR=.\dacapo_outputs"
SET "RESULTS_DIR=.\results"
MKDIR %GC_LOG_DIR% 2>NUL
MKDIR %DACAPO_OUT_DIR% 2>NUL
MKDIR %RESULTS_DIR% 2>NUL

REM --- Διαμορφώσεις προς δοκιμή ---
SET GCS_TO_TEST=G1 Parallel ZGC Shenandoah
SET HEAP_SIZES_TO_TEST=4g 12g
REM Επιλέξτε benchmarks από το DaCapo suite (π.χ. avrora, lusearch, h2, tomcat)
SET BENCHMARKS_TO_TEST=avrora lusearch tomcat

REM --- Κύκλος εκτέλεσης ---
FOR %%G IN (%GCS_TO_TEST%) DO (
    FOR %%H IN (%HEAP_SIZES_TO_TEST%) DO (
        FOR %%B IN (%BENCHMARKS_TO_TEST%) DO (
            ECHO Running GC: %%G, Heap: %%H, Benchmark: %%B

            SET "GC_OPTS="
            IF "%%G"=="G1" ( SET "GC_OPTS=-XX:+UseG1GC" )
            IF "%%G"=="Parallel" ( SET "GC_OPTS=-XX:+UseParallelGC" )
            IF "%%G"=="ZGC" (
                REM ZGC υποστηρίζεται σε Windows από JDK 14+. Σε JDK 11-13 ήταν experimental και όχι για Windows.
                REM Αν χρησιμοποιείτε παλαιότερο JDK που το έχει experimental, προσθέστε: -XX:+UnlockExperimentalVMOptions
                SET "GC_OPTS=-XX:+UseZGC"
            )
            IF "%%G"=="Shenandoah" (
                REM Shenandoah συνήθως απαιτεί OpenJDK builds (π.χ. Adoptium Temurin, Oracle OpenJDK).
                REM Αν χρησιμοποιείτε παλαιότερο JDK που το έχει experimental, προσθέστε: -XX:+UnlockExperimentalVMOptions
                SET "GC_OPTS=-XX:+UseShenandoahGC"
            )

            SET "HEAP_OPTS=-Xms%%H -Xmx%%H"
            SET "LOG_FILE_GC_PATH=!GC_LOG_DIR!\gc_%%G_%%H_%%B.log"
            SET "LOG_FILE_DACAPO_PATH=!DACAPO_OUT_DIR!\dacapo_%%G_%%H_%%B.log"

            REM Unified JVM Logging (Java 9+). Προσαρμόστε τις επιλογές 'tags' και 'level' ανάλογα με τις ανάγκες.
            REM Ορίζουμε το αρχείο καταγραφής για τον GC
            SET "GC_LOG_JVM_OPTS=-Xlog:gc*:file=!LOG_FILE_GC_PATH!:time,level,tags,pid,tid:filecount=5,filesize=100m"

            REM --- Debug: Echo the command (Χρησιμοποιούμε !variable! για delayed expansion) ---
            ECHO Command being executed:
            ECHO !JAVA_CMD! !GC_OPTS! !HEAP_OPTS! !GC_LOG_JVM_OPTS! -jar !DACAPO_JAR! %%B -n 3
            REM --- End Debug ---

            REM Εκτελέστε την εντολή Java. Ανακατεύθυνση εξόδου DaCapo στο δικό της αρχείο.
            "!JAVA_CMD!" !GC_OPTS! !HEAP_OPTS! !GC_LOG_JVM_OPTS! -jar !DACAPO_JAR! %%B -n 3 > "!LOG_FILE_DACAPO_PATH!" 2>&1

            REM Το "-n 3" εκτελεί το benchmark 3 φορές (η DaCapo κάνει αυτόματα warm-up). Προσαρμόστε ανάλογα.

            ECHO Completed GC: %%G, Heap: %%H, Benchmark: %%B
            ECHO -----------------------------------------------------
        )
    )
)
ECHO All benchmarks finished.
ENDLOCAL