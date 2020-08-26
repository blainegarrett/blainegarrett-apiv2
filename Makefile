.PHONY: env
env:
	# TODO: Ensure venv is active and python 3

.PHONY: help
help:
	@echo "TODO: Write the install help"

.PHONY: install
install:
	pipenv install
	pipenv lock -r > requirements.txt

.PHONY: run
dev:
	@echo "Starting Development Server"
	# gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --reload
	GOOGLE_APPLICATION_CREDENTIALS="./private/datastore-service-account.json" REDIS_HOST=127.0.0.1 REDIS_PORT=6379 REDIS_PASSWORD="" uvicorn main:app --reload

.PHONY: redis 
redis:
	docker run  -p 127.0.0.1:6379:6379/tcp --name container-redis-test -d redis

.PHONY: test
test:
	pipenv run pytest tests

.PHONY: deploy
deploy:
	gcloud app deploy --project blaine-garrett --version $(filter-out $@,$(MAKECMDGOALS))

