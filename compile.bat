@echo off
setlocal enabledelayedexpansion
pushd "%~dp0"
if /i "!PROCESSOR_ARCHITECTURE!" equ "AMD64" (
    set "arch_string=nt64"
) else (
    set "arch_string=nt32"
)
set "servername=myvirtualnic_!arch_string!"
pyinstaller -F -c -n "!servername!" -i "NONE" "VirtualNicRunner.py"
rmdir /s /q "build"
del /f /q "!servername!.spec"
call remove_python_cache.bat
echo="compilation finished."
popd
