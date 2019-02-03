all: qclient qserver kclient kserver

kapp: kclient kserver

qclient: src/qclient.py
	python -m py_compile src/qclient.py
	mv src/qclient.pyc qclient
	chmod +x qclient

qserver: src/qserver.py
	python -m py_compile src/qserver.py
	mv src/qserver.pyc qserver
	chmod +x qserver

kclient: src/kclient.py
	python -m py_compile src/kclient.py
	mv src/kclient.pyc kclient
	chmod +x kclient

kserver: src/kserver.py
	python -m py_compile src/kserver.py
	mv src/kserver.pyc kserver
	chmod +x kserver
