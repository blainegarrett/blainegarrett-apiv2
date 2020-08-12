# blainegarrett-apiv2
Python 3.7 REST api for blainegarrett.com leveraging fastapi


## Prerequisites
This project leverages pyenv and pipenv to make python installations and virtual environments respectively.
```
brew install pyenv
pyenv install 3.7.0


brew install pipenv
python --version
pip --version
```

## Initialization
 - Run `gcloud components update` to ensure the latest python components are installed
 - Run `pipenv shell` to switch into python virtual environment
 - Run `make install` to install dependencies and generate requirements.txt 
 - Run `uvicorn main:app --reload` to run the application


