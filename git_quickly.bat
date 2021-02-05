@echo off
setlocal enabledelayedexpansion
pushd "%~dp0"
git status||(
    echo="git status errored."
    goto lastline
)
for /f "usebackq delims=" %%i in (`git status^|find "nothing to commit, working tree clean"`) do (
    echo="nothing to commit, working tree clean."
    goto lastline
)
git add .&&git commit -m m
echo="add and commit finished."

:lastline
popd
