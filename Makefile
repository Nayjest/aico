CONTAINER = aico
DEXEC = docker exec -it $(CONTAINER)
TEST = $(DEXEC) python -m pytest  --log-cli-level=INFO
ifeq ($(I_AM_INSIDE_DOCKER_CONTAINER),true)
	DEXEC =
endif

# ============== [ Container control ] ==============

init:
	docker-compose up -d --build && $(DEXEC) bash
sh:
	$(DEXEC) bash
stop:
	docker-compose stop
cs:
	$(DEXEC) flake8 aico webapp
black:
	$(DEXEC) black aico webapp
# ============== [ Tests ] ==============


install:
	pip install -r requirements/dev.txt

py:
	python -i -c "from aico.main import *; import sys; sys.displayhook = lambda x: exec(['_=x; pprint(x)','pass'][x is None])"


pkg:
	$(DEXEC) python -m build --wheel --sdist .

publish:
	$(DEXEC) twine upload dist/* -u __token__ -p $(PYPI_TOKEN) --verbose
upload: publish