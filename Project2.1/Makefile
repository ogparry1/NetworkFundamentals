all: qclient qserver

qclient: qclient.py
	python -m py_compile qclient.py
	mv qclient.pyc qclient
	chmod +x qclient

qserver: qserver.py
	python -m py_compile qserver.py
	mv qserver.pyc qserver
	chmod +x qserver
