@echo off
REM Version management script for RAG Pipeline
REM Usage: version.bat [command] [options]

if "%1"=="" (
    echo RAG Pipeline Version Manager
    echo Usage: version.bat ^<command^> [options]
    echo.
    echo Commands:
    echo   get                    - Get current version
    echo   set ^<version^>          - Set version
    echo   increment ^<type^>       - Increment version (major^|minor^|patch^)
    echo   info                   - Get detailed version information
    echo   changelog              - Show recent changelog entries
    echo.
    echo Examples:
    echo   version.bat get
    echo   version.bat set 1.2.0
    echo   version.bat increment minor
    echo   version.bat info
    goto :eof
)

python version.py %*
