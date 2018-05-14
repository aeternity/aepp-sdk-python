GIT_DESCR = $(shell git describe)
# build output folder
DIST_FOLDER = dist
BUILD_FOLDER = build

.PHONY: list
list:
	clean build lint test publish-test publish

default: build

workdir:
	mkdir -p dist

build: build-dist

build-dist:
	@echo build 
	python setup.py sdist
	python setup.py bdist_wheel
	@echo done

test: test-all

test-all:
	@echo run pytest
	pytest
	@echo done

lint: lint-all

lint-all:
	@echo lint aeternity
	flake8 aeternity
	@echo done

clean:
	@echo remove '$(DIST_FOLDER)','$(BUILD_FOLDER)' folders
	@rm -rf $(DIST_FOLDER) $(BUILD_FOLDER)
	@echo done  

publish:
	@echo publish on pypi.org
	twine upload dist/*
	@echo done

publish-test:
	@echo publish on test.pypi.org
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	@echo done