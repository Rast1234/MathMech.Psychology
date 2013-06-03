rmdir dist /S /Q
xcopy vlc_libs dist /E /I
cxfreeze main.py --target-dir dist --base-name=Win32GUI --include-modules atexit,PySide.QtNetwork,vlc --icon logo.ico
