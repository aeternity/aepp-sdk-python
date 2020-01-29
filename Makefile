# build output folder
DIST_FOLDER = dist
BUILD_FOLDER = build
# extra test options
TEST_OPTS = ''
# Documentation
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = docs
BUILDDIR      = docs/_build

.PHONY: list
list:
	@echo clean build lint test publish-test publish

default: build

build: build-dist

build-dist:
	@echo build 
	poetry build
	@echo done

install: build
	@echo build and install the SDK
	python -m pip install dist/$(shell ls -tr dist | grep whl | tail -1)
	@echo installation completed

test: test-all

test-all:
	@echo run pytest
	pytest -v --junitxml test-results.xml tests --cov=aeternity --cov-config .coveragerc --cov-report xml:coverage.xml $(TEST_OPTS)
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
	poetry publish --build
	@echo done

publish-test:
	@echo publish on test.pypi.org
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	poetry publish --build --repository testpypi
	@echo done

deps:
	@echo generating requirements.txt
	poetry export --dev -f requirements.txt > requirements.txt
	@echo done

changelog:
	@echo build changelog
	gitolog -t keepachangelog -s angular . -o CHANGELOG.md 
	@echo done

docs-html:
	@echo build html documentation
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo done

docs-view: docs-html
	python -c "import webbrowser; webbrowser.open('docs/_build/html/index.html')"

docs-lint:
	@echo lint documentation
	$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo done

