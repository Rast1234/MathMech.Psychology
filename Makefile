build: mainwindow.ui generate_video_dir
	pyside-uic mainwindow.ui > window.py

run: build main.py
	python2 main.py

generate_video_dir:
	$(if $(wildcard ./video),,mkdir ./video)

