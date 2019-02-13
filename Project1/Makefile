all: qclient qserver

qclient: src/qclient.py
	python -m py_compile src/qclient.py
	mv src/qclient.pyc qclient
	chmod +x qclient

qserver: src/qserver.py
	python -m py_compile src/qserver.py
	mv src/qserver.pyc qserver
	chmod +x qserver
