FLASK_APP = app.py
FLASK_ENV = development

.PHONY: install run clean

install:
	pip install -r requirements.txt

run:
	FLASK_APP=$(FLASK_APP) FLASK_ENV=$(FLASK_ENV) flask run

clean:
	find . -type f -name '*.pyc' -delete