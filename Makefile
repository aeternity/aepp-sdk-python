# build output folder
DIST_FOLDER = dist
BUILD_FOLDER = build

.PHONY: list
list:
	@echo clean build lint test publish-test publish

default: build

build: build-dist

build-dist:
	@echo build 
	python setup.py sdist
	python setup.py bdist_wheel
	@echo done

test: test-all

test-all:
	@echo run pytest
	pytest -v --junitxml test-results.xml tests --cov=aeternity --cov-config .coveragerc --cov-report xml:coverage.xml
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

changelog:
	@echo build changelog
	gitolog -t keepachangelog -s angular . -o CHANGELOG.md 
	@echo done
