# build output folder
DIST_FOLDER = dist
BUILD_FOLDER = build
# extra test options
TEST_OPTS = '-k test_cli_name_claim'

.PHONY: list
list:
	@echo clean build lint test publish-test publish

default: build

build: build-dist

build-dist:
	@echo build 
	poetry build
	@echo done

test: test-all

test-all:
	@echo run pytest
	PYTHONWARNINGS=ignore pytest -v --junitxml test-results.xml tests --cov=aeternity --cov-config .coveragerc --cov-report xml:coverage.xml $(TEST_OPTS)
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

deps:
	@echo generating requirements.txt
	dephell deps convert
	@echo done

changelog:
	@echo build changelog
	gitolog -t keepachangelog -s angular . -o CHANGELOG.md 
	@echo done
