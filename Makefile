PROJECT = homecon
VERSION = $(shell homecon/__version__.py)


.PHONY: image
image:
	docker build --build-arg project=$(PROJECT) -t homecon .
	docker tag homecon homecon:$(VERSION)
	docker save homecon:$(VERSION) > dist/homecon-$(VERSION).tar
