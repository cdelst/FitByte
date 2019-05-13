# FitByte

A project I started as I've been getting more and more interested in data manipulation and study after getting a FitBit Charge 3.  Right now it is a very rudimentary data collector using the FitBit web API :

https://dev.fitbit.com/build/reference/web-api

My goal is to store as much data as physically possible, and after gathering enough, hopefully create some interesting analysis on my life!  As of now, I am collecting and storing my heart, steps, distance, calories, stories, and sleep data locally on my computer.  I plan on adding more as time goes on, and eventually making it completely user-friendly.  

## Getting Started

Recommended with pipenv as an environment manager with python.  Before use, the user has to make a Fitbit Developer account and get two keys:
USERID, and USERSECRET

After getting those, replace the two lines in example_tokens.txt, and rename example_tokens.txt to "tokens.txt" --IMPORTANT

### Running

Package management was done with Pipenv, so it is super easy...

If you do not have pipenv installed, I recommend it, as it makes package-ing very easy with python: [pipenv](https://github.com/pypa/pipenv)

```
pip install pipenv
pipenv shell
pipenv sync
python app.py
```

NOTE: 
requests-oauthlib = "~=1.1.0"
oauthlib = "~=2.1.0"

These package versions are required for the API to work correctly
## Built With

* [Python](https://www.python.org) - Scripting
* [Fitbit API](https://github.com/orcasgit/python-fitbit) - API
* [gather_keys_oauth2.py](https://github.com/orcasgit/python-fitbit/blob/master/gather_keys_oauth2.py) - For Oauth2 Authentification

## Contributing

If you would like to add something to my very basic app, just submit a pull request. 

## Author

* **Case Delst** - [Case Delst](https://github.com/CaseDelst)

## Acknowledgments

* PurpleBooth for this README.md

