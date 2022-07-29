PROJECT = homecon
VERSION = $(shell backend/src/homecon/__version__.py)

.PHONY: image
image:
	npm --prefix frontend run build
	python3 "setup.py" sdist
	docker build --build-arg project=$(PROJECT) --build-arg version=$(VERSION) -t brechtba/homecon .
	docker tag brechtba/homecon brechtba/homecon:$(VERSION)
	docker push brechtba/homecon


.PHONY: push
push:
	docker push brechtba/homecon