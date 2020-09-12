#  FitByte

A project I started as I've been getting more and more interested in data manipulation and study after getting a FitBit Charge 3.  Right now it is a very rudimentary data collector using the FitBit web API :

https://dev.fitbit.com/build/reference/web-api

My goal is to store as much data as physically possible, and after gathering enough, hopefully create some interesting analysis on my life!  As of now, I am collecting and storing my heart, steps, distance, calories, stories, and sleep data locally on my computer.  I plan on adding more as time goes on, and eventually making it completely user-friendly.  

So far I have implemented features that make my everyday logging of data easier, such as a date-last-called feature, as well as a completely functional sync-up-to feature that syncs from the last called date all the way up to the date you enter.  

# # Getting Started

Recommended with pipenv as an environment manager with python.  Before use, the user has to make a Fitbit Developer account and get two keys:
USERID, and USERSECRET

To get those keys, you will need to use an OAuth2 library.  It is easiest to download the file and put it in the same directory as the app. 
[This](https://github.com/orcasgit/python-fitbit/blob/master/gather_keys_oauth2.py) is a link to the GitHub.  

After getting those, replace the two lines in example_tokens.txt, and rename example_tokens.txt to "tokens.txt" --IMPORTANT

As of now, you will have to have a file named data with this structure in it in the same file as your script:

-data  <br>
&nbsp;&nbsp;&nbsp;&nbsp;-Calories  <br>
&nbsp;&nbsp;&nbsp;&nbsp;-Distance  <br>
&nbsp;&nbsp;&nbsp;&nbsp;-Elevation  <br>
&nbsp;&nbsp;&nbsp;&nbsp;-Heart  <br>
&nbsp;&nbsp;&nbsp;&nbsp;-Sleep  <br>
&nbsp;&nbsp;&nbsp;&nbsp;-Steps  <br>
&nbsp;&nbsp;&nbsp;&nbsp;-SummaryData  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ ActivitySummary.csv  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ FoodSummary.csv<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ SleepSummary.csv


# ## Running

Package management was done with Pipenv, so it is super easy...

If you do not have pipenv installed, I recommend it, as it makes package-ing very easy with python: [pipenv](https://github.com/pypa/pipenv)

```
pip install pipenv
pipenv shell
pipenv sync
python app.py
```

NOTE: 

YOU MUST HAVE EXACTLY THESE DEPENDENCIES INSTALLED FOR THE FITBIT API TO WORK PROPERLY

requests-oauthlib = 1.1.0

oauthlib = 2.1.0

These package versions are required for the API to work correctly

# # Built With

* [Python](https://www.python.org) - Scripting
* [Fitbit API](https://github.com/orcasgit/python-fitbit) - API
* [gather_keys_oauth2.py](https://github.com/orcasgit/python-fitbit/blob/master/gather_keys_oauth2.py) - For Oauth2 Authentification
* [pyfiglet](https://www.devdungeon.com/content/create-ascii-art-text-banners-python) - For Word Art On Launch

# # Contributing

If you would like to add something to my very basic app, just submit a pull request. 

# # Author

* **Case Delst** - [Case Delst](https://github.com/CaseDelst)

# # Acknowledgments

* PurpleBooth for this README.md

