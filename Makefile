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
	#gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --reload
	uvicorn main:app --reload

.PHONY: deploy
deploy:
	gcloud app deploy --project blaine-garrett --version ooo