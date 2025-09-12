#!/bin/bash
dir="./domain"

echo !!!RUFF FORMAT: $dir
ruff format $dir
echo ---------------
echo !!!RUFF SORT: $dir
ruff check --select I --fix $dir
echo ---------------
echo !!!RUFF FIX: $dir
ruff check --fix $dir
echo ---------------
echo !!!MYPY: $dir
mypy $dir
#echo !!!TESTING:
#pytest .