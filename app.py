"""
Callback URL - https://127.0.0.1:8080/
OAuth 2.0: Authorization URI - https://www.fitbit.com/oauth2/authorize
OAuth 2.0: Access/Refresh Token Request URI - https://api.fitbit.com/oauth2/token

DOCUMENTATION:
https://python-fitbit.readthedocs.io/en/latest/

Epoch of Watch: 4/30/19 

ToDo : 
    1. Fix the sleep summary data DONE
    2. Get more data
    3. Make the code prettier and push to git

"""



import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd 
from datetime import datetime
import time
import matplotlib.pyplot as plt
import os.path
import csv

def main():
    
    #Eliminates the unneeded waiting for the server, refreshes every 10 min
    with open('tokens.txt') as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    dt = int(time.time())
    lastdt = int(content[2])
    expireTime = 10 * 60  #10 minutes in UNIX

    #ME specific data, read from line 1 and 2 of tokens file
    CLIENT_ID = content[0]
    CLIENT_SECRET = content[1]

    timeLastCalled(dt, lastdt)
    if((dt - lastdt) >= expireTime):
        print('Calling server for new tokens\n')
        server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
        server.browser_authorize()
        
        ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
        REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
        
        print('Writing new tokens to tokens.txt\n')
        with open('tokens.txt', 'w') as f:
            f.write(str(CLIENT_ID) + '\n')
            f.write(str(CLIENT_SECRET) + '\n')
            f.write(str(dt) + '\n')
            f.write(str(ACCESS_TOKEN) + '\n')
            f.write(str(REFRESH_TOKEN) + '\n')
    else:
        ACCESS_TOKEN = content[3]
        REFRESH_TOKEN = content[4]

    auth2_client = fitbit.Fitbit(CLIENT_ID, 
                                CLIENT_SECRET, 
                                oauth2=True, 
                                access_token=ACCESS_TOKEN, 
                                refresh_token=REFRESH_TOKEN)

    #Gets date from user
    userDate = str(input('Input Target Date (YYYYMMDD):'))
    userDate2 = userDate[0:4] + '-' + userDate[4:6] + '-' + userDate[6:]

    #Heartrate
    fit_statsHR = auth2_client.intraday_time_series('activities/heart', base_date=userDate2, detail_level='1sec')
    intradayDataCollection(fit_statsHR, 
                           'activities-heart-intraday',
                           'Heart',
                           userDate)

    #Distance
    fit_statsDST = auth2_client.intraday_time_series('activities/distance', base_date=userDate2, detail_level='1min')
    intradayDataCollection(fit_statsDST, 
                           'activities-distance-intraday',
                           'Distance',
                           userDate)

    #Steps
    fit_statsSTP = auth2_client.intraday_time_series('activities/steps', base_date=userDate2, detail_level='1min')
    intradayDataCollection(fit_statsSTP, 
                           'activities-steps-intraday',
                           'Steps',
                           userDate)

    #Elevation
    fit_statsELE = auth2_client.intraday_time_series('activities/elevation', base_date=userDate2, detail_level='1min')
    intradayDataCollection(fit_statsELE, 
                           'activities-elevation-intraday',
                           'Elevation',
                           userDate)
    
    #Calories
    fit_statsCAL = auth2_client.intraday_time_series('activities/calories', base_date=userDate2, detail_level='1min')
    intradayDataCollection(fit_statsCAL, 
                           'activities-calories-intraday',
                           'Calories',
                           userDate)
    
    #Sleep
    fit_statsSLE = auth2_client.sleep(date=userDate2)
    stime_list = []
    sval_list = []

    for i in fit_statsSLE['sleep'][0]['minuteData']:
        stime_list.append(i['dateTime'])
        sval_list.append(i['value'])

    sleepDF = pd.DataFrame({'Time':stime_list, 'State':sval_list})
    sleepDF['Interpreted'] = sleepDF['State'].map({'2':'Awake', '3':'Very Awake', '1':'Asleep'})
    writeToFile(sleepDF, 'Sleep', 'Sleep', userDate, True, True, False)

    #Sleep summary data
    if str(input("Add date to sleep summary? y / n: ")) == 'y':
        fit_statsSum = auth2_client.sleep(date=userDate2)['sleep'][0]
        ssummarydf = pd.DataFrame({'Date':fit_statsSum['dateOfSleep'],
                    'MainSleep':fit_statsSum['isMainSleep'],
                    'Efficiency':fit_statsSum['efficiency'],
                    'Duration':fit_statsSum['duration'],
                    'Minutes Asleep':fit_statsSum['minutesAsleep'],
                    'Minutes Awake':fit_statsSum['minutesAwake'],
                    'Awakenings':fit_statsSum['awakeCount'],
                    'Restless Count':fit_statsSum['restlessCount'],
                    'Restless Duration':fit_statsSum['restlessDuration'],
                    'Time in Bed':fit_statsSum['timeInBed']
                                } ,index=[0])
        tempPath = os.path.join(os.getcwd(), 'data', 'SummaryData', 'SleepSummary.csv')
        tempPath2 = os.path.join(os.getcwd(), 'data', 'SummaryData', 'SleepSummary1.csv')

        with open(tempPath,'a') as f:
            if(str(input('First? y / n: ')) == 'y'):
                ssummarydf.to_csv(f, header=True, index=False)
            else:
                ssummarydf.to_csv(f, header=False, index=False)
        
        #No idea why but outputting to CSV skips a line every fucking time
        fixFuckingWhiteSpaces(tempPath, tempPath2)
    


#Takes a DF and writes it to the folder with the file name
def fixFuckingWhiteSpaces (inPath, outPath):
    with open(inPath) as input, open(outPath, 'w', newline='') as output:
        writer = csv.writer(output)
        for row in csv.reader(input):
            if any(field.strip() for field in row):
                writer.writerow(row)
    os.remove(inPath)
    os.rename(outPath, inPath)

def intradayDataCollection(raw, type, datatype, userDate):
    timeList = []
    dataList = [] 

    for i in raw[type]['dataset']:
        dataList.append(i['value'])
        timeList.append(i['time'])
    df = pd.DataFrame({'Time' :timeList, datatype : dataList,})
    writeToFile(df, datatype, datatype, userDate, True, True, False)

#Takes a data structure and saves it to a csv
def writeToFile(df, name, folder, date, ind, head, overwrite):
    fileName = date + '_' + name + '.csv'
    basePath = os.path.join(os.getcwd(), 'data', folder)
    fullPath = os.path.join(basePath, fileName)
    if not (os.path.isfile(fullPath)) or overwrite:
        df.to_csv(fullPath, index=ind, header=head)

#Little function to tell the user how long ago they submitted a token refresh
def timeLastCalled(current, lastCall):
    diff = int(current - lastCall)
    days = int(diff / (24 * 60 * 60))
    diff -= (days * 86400)
    hours = int(diff / (60 * 60))
    diff -= (hours * 360)
    minutes = int(diff / 60)
    seconds = diff - (minutes * 60)
    print('Last call was: ' + str(days) + ' Day(s), ' + str(hours) + ' Hour(s), ' + str(minutes) + ' Minute(s), and ' + str(seconds) + ' Second(s) ago')

if __name__ == "__main__":
    main()