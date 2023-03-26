rem This script is a helper to easily call
rem the main.py file with a python interpreter
set "root_dir=%~dp0"
python "%root_dir%\src\main.py" %*
