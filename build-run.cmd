@echo off
copy /B /Y main.py main.pyw 1>NUL
pyside-uic mainwindow.ui > window.py
REM start main.pyw
main.py