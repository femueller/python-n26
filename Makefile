PROJECT = "n26"

current-version:
	@echo "Current version is `cat ${PROJECT}/__init__.py | grep '__version__' | cut -d ' ' -f3 | sed s/\'//g`"

build:
	git stash
	python setup.py sdist
	- git stash pop

test:
	pipenv run pytest

upload:
	# Upload to Gemfury
	#	curl -F package=@dist/`ls -t1 dist/ | grep tar.gz | head -n1` https://gems.gemfury.com/<gem fury tokena
	# Upload to PyPI
	python setup.py sdist upload -r pypi

git-release:
	git add ${PROJECT}/__init__.py
	git commit -m "Bumped version to `cat ${PROJECT}/__init__.py | grep '__version__' | cut -d ' ' -f3 | sed s/\'//g`"
	git tag `cat ${PROJECT}/__init__.py | grep '__version__' | cut -d ' ' -f3 | sed s/\'//g`
	git push
	git push --tags

_release-patch:
	@echo "version = \"`cat ${PROJECT}/__init__.py | awk -F '("|")' '{ print($$2)}' | awk -F. '{$$NF = $$NF + 1;} 1' | sed 's/ /./g'`\"" > ${PROJECT}/__init__.py
release-patch: _release-patch git-release build upload current-version

_release-minor:
	@echo "version = \"`cat ${PROJECT}/__init__.py | awk -F '("|")' '{ print($$2)}' | awk -F. '{$$(NF-1) = $$(NF-1) + 1;} 1' | sed 's/ /./g' | awk -F. '{$$(NF) = 0;} 1' | sed 's/ /./g' `\"" > ${PROJECT}/__init__.py
release-minor: _release-minor git-release build upload current-version

_release-major:
	@echo "version = \"`cat ${PROJECT}/__init__.py | awk -F '("|")' '{ print($$2)}' | awk -F. '{$$(NF-2) = $$(NF-2) + 1;} 1' | sed 's/ /./g' | awk -F. '{$$(NF-1) = 0;} 1' | sed 's/ /./g' | awk -F. '{$$(NF) = 0;} 1' | sed 's/ /./g' `\"" > ${PROJECT}/__init__.py
release-major: _release-major git-release build upload current-version

release: release-patch
