all: contestmeister contestant cserver

clean:
	rm contestmeister contestant cserver cbank

contestmeister: contestmeister.py
	python -m py_compile contestmeister.py
	mv contestmeister.pyc contestmeister
	chmod +x contestmeister

contestant: contestant.py
	python -m py_compile contestant.py
	mv contestant.pyc contestant
	chmod +x contestant

cserver: cserver.py
	python -m py_compile cserver.py
	mv cserver.pyc cserver
	chmod +x cserver
