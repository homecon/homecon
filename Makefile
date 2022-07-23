PROJECT = homecon
VERSION = $(shell backend/src/homecon/__version__.py)


.PHONY: image
image:
	cd frontend
	npm run build
	cd ..
	python3 "setup.py" sdist
	docker build --build-arg project=$(PROJECT) -t brechtba/homecon .
	docker tag brechtba/homecon brechtba/homecon:$(VERSION)
	docker push brechtba/homecon
