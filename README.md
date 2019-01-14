# Boston Microgreens Grow App
Onboarding guide and project structure

## Installing Virtual Environment
We'll be using a virtual environment for dependency management in this project.
To create the virtual environment, first make sure Python 3.6 is installed. Then run:
```
python3.6 -m venv virtualenv
source virtualenv/bin/activate
pip install -r requirements.txt
```
    
The environment can be named whatever you want, and it doesn't have to live in the project directory either (I like to 
keep mine in `~/.virtualenvs`). Just make sure that your IDE is configured to use the Python Interpreter belonging to 
your virtual env, and that none of your virtual env files enter version control.

To add a new dependency to the project just run `pip freeze > requirements.txt`

## Project Structure
The project follows the structure of a standard Django project for the most part -- consult the docs if you need more
info. The `functional tests/` directory contains only a `tests.py` file because all it does is run automated web 
browser tests on the entire application. In your IDE, be sure to make a _Run Configuration_ for `python manage.py test 
functional_tests` so that you can run those tests immediately.