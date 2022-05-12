PROJECT = homecon
VERSION = $(shell backend/src/homecon/__version__.py)


.PHONY: image
image:
	docker build --build-arg project=$(PROJECT) -t brechtba/homecon .
	docker tag brechtba/homecon brechtba/homecon:$(VERSION)
