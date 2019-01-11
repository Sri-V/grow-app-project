# Boston Microgreens Grow App

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