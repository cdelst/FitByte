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
from calendar import monthrange #For days in the month


def main():
    
    #Opens tokens.txt to read the different lines of user-specific data
    with open('tokens.txt') as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    #Sets up the date-time for the refresh if-statement
    dt = int(time.time())
    lastdt = int(content[2])
    expireTime = 10 * 60  #10 minutes in UNIX

    #User specific data, read from line 1 and 2 of tokens file
    CLIENT_ID = content[0]
    CLIENT_SECRET = content[1]

    #Print Days, Hours, Minutes, Seconds since last server refresh
    timeLastCalled(dt, lastdt)

    #Determine if a new server call is required to refresh tokens
    if((dt - lastdt) >= expireTime): #If time last called was greater than 10 minutes ago
        
        print('Calling server for new tokens...\n')
        server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
        server.browser_authorize()
        
        ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
        REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
        
        print('Writing new tokens to tokens.txt\n')
        
        #Writes updated information to tokens.txt for next run of program
        with open('tokens.txt', 'w') as f:                                                              #Writes the dependencies into 'tokens.txt' for program runtime           
            f.write(str(CLIENT_ID) + '\n')
            f.write(str(CLIENT_SECRET) + '\n')
            f.write(str(dt) + '\n')
            f.write(str(ACCESS_TOKEN) + '\n')
            f.write(str(REFRESH_TOKEN) + '\n')
    else:                                                                                               #Else use the tokens from tokens.txt and don't call server, saves time
        ACCESS_TOKEN = content[3]
        REFRESH_TOKEN = content[4]

    auth2_client = fitbit.Fitbit(CLIENT_ID,                                                             #Authentication of FitBit App
                                CLIENT_SECRET, 
                                oauth2=True, 
                                access_token=ACCESS_TOKEN, 
                                refresh_token=REFRESH_TOKEN)

    #Gets date from user
    userDate = str(input('\nInput Target Date (YYYYMMDD):'))
    
    month = userDate[4:6]
    day = userDate[6:]
    if day[0] == '0':                                                           #Takes out '01' to '1'
        day2 = day[1]
    else: day2 = day
    year = userDate[0:4]
    
    userDate2 = year + '-' + month + '-' + day
    formalDate = month + '/' + day + '/' + year
    formalDateSpreadsheet = month + '/' + day2 + '/' + year


    #Heartrate
    fit_statsHR = auth2_client.intraday_time_series('activities/heart',                                 #Calls intraday heart series, interval = 1 sec
                                                     base_date=userDate2, 
                                                     detail_level='1sec')
    intradayDataCollection(fit_statsHR, 
                          'activities-heart-intraday',
                          'Heart',
                           userDate)

    #Distance
    fit_statsDST = auth2_client.intraday_time_series('activities/distance',                             #Calls intraday distance series, interval = 1min
                                                      base_date=userDate2, 
                                                      detail_level='1min')
    intradayDataCollection(fit_statsDST, 
                          'activities-distance-intraday',
                          'Distance',
                           userDate)

    #Steps
    fit_statsSTP = auth2_client.intraday_time_series('activities/steps',                                #Calls intraday steps series, interval = 1min
                                                      base_date=userDate2, 
                                                      detail_level='1min')
    intradayDataCollection(fit_statsSTP, 
                           'activities-steps-intraday',
                           'Steps',
                           userDate)

    #Elevation
    fit_statsELE = auth2_client.intraday_time_series('activities/elevation',                            #Calls intraday elevation series, interval = 1min
                                                      base_date=userDate2, 
                                                      detail_level='1min')
    intradayDataCollection(fit_statsELE, 
                           'activities-elevation-intraday',
                           'Elevation',
                           userDate)
    
    #Calories
    fit_statsCAL = auth2_client.intraday_time_series('activities/calories',                             #Calls intraday calories series, interval = 1min
                                                      base_date=userDate2, 
                                                      detail_level='1min')
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

    sleepDF = pd.DataFrame({'Time':stime_list, 
                            'State':sval_list})
    sleepDF['Interpreted'] = sleepDF['State'].map({'2':'Awake', 
                                                   '3':'Very Awake', 
                                                   '1':'Asleep'})
    writeToFile(sleepDF, 'Sleep', 'Sleep', userDate, True, True, False)

    #Sleep summary data

    sleepSumPath = os.path.join(os.getcwd(), 'data','SummaryData', 'SleepSummary.csv')
    sleepSumPath2 = os.path.join(os.getcwd(), 'data', 'SummaryData', 'SleepSummary1.csv')
    
    #FIX THIS, NOT WORKING
    sleepNotInputted = True
    with open(sleepSumPath,'a') as f:
            tempSleepDF = pd.read_csv(sleepSumPath)
            for i in tempSleepDF['Date']:
                print('Comparing: ' + i + ' and ' + formalDateSpreadsheet)
                if type(i) == str and i == formalDateSpreadsheet:
                    
                    print('2 Dates are similar')
                    sleepNotInputted = False


    if sleepNotInputted:
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
                                   'Time in Bed':fit_statsSum['timeInBed']} ,index=[0])
       
        sleepSumPath = os.path.join(os.getcwd(), 'data','SummaryData', 'SleepSummary.csv')
        sleepSumPath2 = os.path.join(os.getcwd(), 'data', 'SummaryData', 'SleepSummary1.csv')

        
        with open(sleepSumPath,'a') as f:
            tempSleepDF = pd.read_csv(sleepSumPath)                                                     #Sets up file to be checked for header value
            sleepSumExists = tempSleepDF.empty                                                          #Checks the file to see if it's empty
            ssummarydf.to_csv(f, header=sleepSumExists, index=False)                                    #Writes the summary data to 
        
        #No idea why but outputting to CSV skips a line every fucking time
        fixWhiteSpaces(sleepSumPath, sleepSumPath2)
    

    #Activity Summary
    if str(input("Add date to activity summary? y / n: ")) == 'y':
        sumFitStatsACT = auth2_client.activities(date=userDate2)['summary']
        actSumDF = pd.DataFrame({'Date':formalDate,
                                 'Activity Calories':sumFitStatsACT['activityCalories'],
                                 'Calories BMR':sumFitStatsACT['caloriesBMR'],
                                 'Calories Out':sumFitStatsACT['caloriesOut'],
                                 'Marginal Calories':sumFitStatsACT['marginalCalories'],
                                 'Elevation':sumFitStatsACT['elevation'],
                                 'Sedentary Minutes':sumFitStatsACT['sedentaryMinutes'],
                                 'Lightly Active Minutes':sumFitStatsACT['lightlyActiveMinutes'],
                                 'Fairly Active Minutes':sumFitStatsACT['fairlyActiveMinutes'],
                                 'Very Active Minutes':sumFitStatsACT['veryActiveMinutes'],
                                 'Floors':sumFitStatsACT['floors'],
                                 'Steps':sumFitStatsACT['steps']} ,index=[0])
        
        actSumPath = os.path.join(os.getcwd(), 'data', 'SummaryData', 'ActivitySummary.csv')
        actSumPath2 = os.path.join(os.getcwd(), 'data', 'SummaryData', 'ActivitySummary1.csv')

        with open(actSumPath,'a') as f:
            tempActivityDF = pd.read_csv(actSumPath)                                                     #Sets up file to be checked for header value
            activitySumExists = tempActivityDF.empty                                                     #Checks the file to see if it's empty
            ssummarydf.to_csv(f, header=sleepSumExists, index=False)                                     #Writes the summary data to 
        
        #No idea why but outputting to CSV skips a line every fucking time
        fixWhiteSpaces(actSumPath, actSumPath2)


#Takes a DF and writes it to the folder with the file name
def fixWhiteSpaces(inPath, outPath):
    
    with open(inPath) as input, open(outPath, 'w', newline='') as output:
        writer = csv.writer(output)
        for row in csv.reader(input):
            if any(field.strip() for field in row):
                writer.writerow(row)
    os.remove(inPath)
    os.rename(outPath, inPath)


#Correctly formats and stores the Panda Dataframes given to the function
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


#Function to tell the user how long ago they submitted a token refresh
def timeLastCalled(current, lastCall):
    diff = int(current - lastCall)
    days = int(diff / (24 * 60 * 60))
    diff -= (days * 86400)
    hours = int(diff / (60 * 60))
    diff -= (hours * 3600)
    minutes = int(diff / 60)
    seconds = diff - (minutes * 60)
    
    print('-----------------------------------------------------------------------------')
    print('Last call was: ' + str(days) + ' Day(s), ' + str(hours) + ' Hour(s), ' + str(minutes) + ' Minute(s), and ' + str(seconds) + ' Second(s) ago')
    print('No refresh needed' if (days == 0 and hours == 0 and minutes < 10) 
                              else 'Server call required')
    print('-----------------------------------------------------------------------------')


#Checks if the summary data is already in the spreadsheet, to not add duplicates
#def checkAlreadyInputted():


#Main:
if __name__ == "__main__":
    main()