.PHONY: build
build:
	docker-compose build

.PHONY: dev
dev:
	docker-compose run api