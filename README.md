# uplift-backend

Technologies involved include:
1. Flask
2. GraphQL (Graphene)

## Setup Instructions

### Virtualenv

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables
It's recommended to use [`autoenv`](https://github.com/kennethreitz/autoenv).
The required environment variables for this API are the following:

````bash
export FLASK_ENV=development
export DB_USERNAME=CHANGE_ME
export DB_PASSWORD=CHANGE_ME
export DB_HOST=localhost
export DB_NAME=upliftdb
export APP_SETTINGS=src.config.DevelopmentConfig
export CLIENT_ID=CHANGE_ME
````

To use `autoenv` with this repository, run the following and set the variables appropriately.

````bash
cp env.template .env
````

### Service Account Key
Check the `#uplift-backend` channel for the `service-account-key.json` which should be placed in the root directory.

## Running the App and Test Suite

To run the app:
````bash
flask run
````

To run the test suite:
````bash
python -m unittest src.tests.test_scraper
````

## Setting up linter
**Flake 8**: Install [flake8](http://flake8.pycqa.org/en/latest/)

**Black**: Either use [command line tool](https://black.readthedocs.io/en/stable/installation_and_usage.html) or use [editor extension](https://black.readthedocs.io/en/stable/editor_integration.html). 

If using VS Code, install the 'Python' extension and include following snippet inside `settings.json`:
```  json
"python.linting.pylintEnabled": false,
"python.linting.flake8Enabled": true,
"python.formatting.provider": "black"
 ```