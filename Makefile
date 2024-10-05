.PHONY: build run build-run stop dev ssh

build:
	docker build -t mock-this-ai .

run:
	docker run -d -p 80:80 --name "mock-this-ai" mock-this-ai

build-run:
	docker run -d -p 80:80 --name "mock-this-ai" mock-this-ai

stop:
	docker stop mock-this-ai && docker rm mock-this-ai

dev-start:
	docker run -d -p 80:80 -v $$(pwd):/app --name "mock-this-ai-dev" mock-this-ai

dev-ssh:
	docker exec -it mock-this-ai-dev /bin/bash

dev-stop:
	docker stop mock-this-ai-dev && docker rm mock-this-ai-dev

ssh:
	docker exec -it mock-this-ai /bin/bash

dev-generate:
	docker exec -it mock-this-ai-dev python3 main.py --input input/openapi.yml

dev-clean:
	docker exec -it mock-this-ai-dev "cd deploy && serverless remove --stage dev"