@echo off
'sync.bat "C:\Source" "C:\Destination" --verbose --2sync --use-content --hverify
:: Function to compute MD5 hash of a file
:ComputeMD5
setlocal enabledelayedexpansion
set "file=%1"
for /f "tokens=* usebackq" %%A in (`certutil -hashfile "%file%" MD5 ^| find /I /V "CertUtil"`) do (
    set "hash=%%A"
)
echo !hash: =!
endlocal & set "md5hash=%hash: =%"

:: Function to verify MD5 hashes
:VerifyMD5
set "src=%1"
set "dst=%2"
setlocal enabledelayedexpansion

set "all_files="
for /r "%src%" %%F in (*) do (
    set "relpath=%%~pnF"
    set "relpath=!relpath:%src%=!"
    if "!all_files!" neq "" (
        set "all_files=!all_files!;"
    )
    set "all_files=!all_files!!relpath!"
)
for /r "%dst%" %%F in (*) do (
    set "relpath=%%~pnF"
    set "relpath=!relpath:%dst%=!"
    if "!all_files!" neq "" (
        set "all_files=!all_files!;"
    )
    set "all_files=!all_files!!relpath!"
)

setlocal enabledelayedexpansion
set "match=true"
for %%F in (!all_files:;= !) do (
    set "srcfile=%src%%%F"
    set "dstfile=%dst%%%F"
    if exist "!srcfile!" if exist "!dstfile!" (
        call :ComputeMD5 "!srcfile!"
        set "src_md5=!md5hash!"
        call :ComputeMD5 "!dstfile!"
        set "dst_md5=!md5hash!"
        if "!src_md5!" neq "!dst_md5!" (
            set "match=false"
            echo MD5 mismatch for %%F: !src_md5! (source) vs !dst_md5! (destination)
        ) else (
            echo MD5 match for %%F: !src_md5!
        )
    ) else (
        set "match=false"
        echo File %%F is not present in both source and destination
    )
)
if "!match!" == "true" (
    echo All files are synchronized (MD5 hashes match).
) else (
    echo Some files are not synchronized (MD5 hashes do not match).
)
endlocal

:end
exit /b 0

:: Main script starts here
set "source=%~1"
set "destination=%~2"
set "verbose=false"
set "purge=false"
set "forcecopy=false"
set "use_ctime=false"
set "use_content=false"
set "two_way=false"
set "hverify=false"

:parse_args
shift
if "%~1"=="" goto :copy_files
if "%~1"=="--verbose" set "verbose=true"
if "%~1"=="--purge" set "purge=true"
if "%~1"=="--forcecopy" set "forcecopy=true"
if "%~1"=="--use-ctime" set "use_ctime=true"
if "%~1"=="--use-content" set "use_content=true"
if "%~1"=="--2sync" set "two_way=true"
if "%~1"=="--hverify" set "hverify=true"
goto :parse_args

:copy_files
if not exist "%destination%" (
    mkdir "%destination%"
    if "%verbose%"=="true" echo Created target directory: %destination%
)

set "robocopy_flags=/E /DCOPY:T"
if "%purge%"=="true" set "robocopy_flags=%robocopy_flags% /PURGE"
if "%forcecopy%"=="true" set "robocopy_flags=%robocopy_flags% /COPYALL"
if "%use_ctime%"=="true" set "robocopy_flags=%robocopy_flags% /TIMFIX"
if "%use_content%"=="true" set "robocopy_flags=%robocopy_flags% /FFT"
if "%verbose%"=="true" set "robocopy_flags=%robocopy_flags% /V"

robocopy "%source%" "%destination%" %robocopy_flags%
if "%two_way%"=="true" robocopy "%destination%" "%source%" %robocopy_flags%

if "%hverify%"=="true" call :VerifyMD5 "%source%" "%destination%"

exit /b 0

