<h1>FitByte</h1>

This is a project I started as I've been getting more and more interested in data manipulation and study after getting a FitBit Charge 3.  Right now it is a very rudimentary data collector using the FitBit web API :

https://dev.fitbit.com/build/reference/web-api

My goal is to store as much data as physically possible, and after gathering enough, hopefully create some interesting analysis on my life!

<h2>If you are interested in using yourself: </h2>

<ol>
<li>You will need a FitBit developer account with personal Client ID and Secret</li>
<li>A tokens.txt file with the exact following format:
    <ol>
    <li>CLIENT_ID</li>
    <li>CLIENT_SECRET</li>
    <li>Current UNIX time</li>
    <li>ACCESS_TOKEN (Acquired through Oauth2)</li>
    <li>REFRESH_TOKEN(Acquired through Oauth2)</li>
    </ol>
</li>
<li>All packages and dependencies installed (See pipfile)
    <ol>
    <li>NOTE: Must have 
        requests-oauthlib = "~=1.1.0" and
        oauthlib = "~=2.1.0" to run without server errors</li>
    </ol>
</li>
<li>Directories created according to the data you want to store</li>
<li>Have fun!</li>
</ol>