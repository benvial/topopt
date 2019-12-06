#
# ifeq ($(TRAVIS_OS_NAME),windows)
# 	SHELL := cmd
# else
# 	SHELL := /bin/bash
# endif

SHELL := /bin/bash


default:
	@echo "\"make save\"?"



gh:
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "master" ]; then exit 1; fi
	@echo "Pushing to github..."
	git add -A
	@read -p "Enter commit message: " MSG; \
	git commit -a -m "$$MSG"
	git push


clean: rmonelab rmtmp
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$\)" | xargs rm -rf
	- rm -rf .ipynb_checkpoints
	- rm -f .app*

run:
	jupyter notebook --no-browser &
	sleep 3 && $(BROWSER) http://localhost:8888/apps/app.ipynb



lstmp:
	@find . -type d -name 'tmp*'


rmtmp:
	@find . -type d -name 'tmp*' | xargs rm -rf


lsonelab:
	@find . -type f -name '*.pos' -o -name '*.pre' -o -name '*.msh' -o -name '*.res'

rmonelab:
	@find . -type f -name '*.pos' -o -name '*.pre' -o -name '*.msh' -o -name '*.res' | xargs rm -f

lint:
	flake8 .

style:
	@echo "Styling..."
	black .

save: clean style gh
