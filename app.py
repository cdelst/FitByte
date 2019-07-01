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

IMPLEMENT https://www.devdungeon.com/content/create-ascii-art-text-banners-python

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

#Implement automatic date system:
    # Get starting and ending date
    # Make an array out of the dates inbetween to make it easier 
    # FINISH -=-=-=--==--=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def main():

    #Creates the client to access API, see function below
    auth2_client = getAuth2Client()
    
    #Saves the last called date for automatic retrieval
    lastCalledDate = printLastSynced(os.listdir("data\\Heart\\"), False)

    #Gets latest date from user
    userDate = str(input('\nInput Target Date (YYYYMMDD): '))
    print()
    
    dateArray = getDateArray(lastCalledDate, userDate)


    #Loops through all dates from lastSynced to current user input
    for dateItem in dateArray:
        
        print("Calling Date: " + dateItem)
        
        date = createDateFormats(dateItem)

        #Heartrate
        intradayDataCollection('activities/heart',
                                auth2_client,
                                date['dashDate'], 
                                '1sec', 
                                'activities-heart-intraday',
                                'Heart',
                                dateItem)
        #Distance
        intradayDataCollection('activities/distance',
                                auth2_client,
                                date['dashDate'],                            
                                '1min',                             
                                'activities-distance-intraday',
                                'Distance',
                                dateItem)
        #Steps
        intradayDataCollection('activities/steps',  
                                auth2_client,                              #Calls intraday steps series, interval = 1min
                                date['dashDate'], 
                                '1min',
                                'activities-steps-intraday',
                                'Steps',
                                dateItem)
        #Elevation
        intradayDataCollection('activities/elevation', 
                                auth2_client,
                                date['dashDate'], 
                                '1min',
                                'activities-elevation-intraday',
                                'Elevation',
                                dateItem)
        #Calories
        intradayDataCollection('activities/calories', 
                                auth2_client,
                                date['dashDate'], 
                                '1min',
                                'activities-calories-intraday',
                                'Calories',
                                dateItem)
        
        #Sleep
        fit_statsSLE = auth2_client.sleep(date=date['dashDate'])
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
        writeToFile(sleepDF, 'Sleep', 'Sleep', dateItem, True, True, False)


        #SLEEP SUMMARY
        sleepSumPath = os.path.join(os.getcwd(), 'data','SummaryData', 'SleepSummary.csv')
        sleepSumPath2 = os.path.join(os.getcwd(), 'data', 'SummaryData', 'SleepSummary1.csv')
        
        if checkInputStatus(sleepSumPath, date, 'Sleep'):
            fit_statsSum = auth2_client.sleep(date=date['dashDate'])['sleep'][0]
            ssummarydf = pd.DataFrame({'Date':fit_statsSum['dateOfSleep'],
                                    'StartTime':fit_statsSum['startTime'][11:19],
                                    'MainSleep':fit_statsSum['isMainSleep'],
                                    'Efficiency':fit_statsSum['efficiency'],
                                    'Duration':fit_statsSum['duration'],
                                    'Minutes Asleep':fit_statsSum['minutesAsleep'],
                                    'Minutes Awake':fit_statsSum['minutesAwake'],
                                    'Awakenings':fit_statsSum['awakeCount'],
                                    'Restless Count':fit_statsSum['restlessCount'],
                                    'Restless Duration':fit_statsSum['restlessDuration'],
                                    'Time in Bed':fit_statsSum['timeInBed']} ,index=[0])
        
            with open(sleepSumPath,'a') as f:
                tempSleepDF = pd.read_csv(sleepSumPath)                                                     #Sets up file to be checked for header value
                sleepSumExists = tempSleepDF.empty                                                          #Checks the file to see if it's empty
                ssummarydf.to_csv(f, header=sleepSumExists, index=False)                                    #Writes the summary data to file
            #No idea why but outputting to CSV skips a line every fucking time
            fixWhiteSpaces(sleepSumPath, sleepSumPath2)
        

        #ACTIVITY SUMMARY
        actSumPath = os.path.join(os.getcwd(), 'data', 'SummaryData', 'ActivitySummary.csv')
        actSumPath2 = os.path.join(os.getcwd(), 'data', 'SummaryData', 'ActivitySummary1.csv')

        if checkInputStatus(actSumPath, date, 'Activity'):
            sumFitStatsACT = auth2_client.activities(date=date['dashDate'])['summary']
            actSumDF = pd.DataFrame({'Date':date['spreadDate'],
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
            
            with open(actSumPath,'a') as f:
                tempActivityDF = pd.read_csv(actSumPath)                                                     #Sets up file to be checked for header value
                activitySumExists = tempActivityDF.empty                                                     #Checks the file to see if it's empty
                actSumDF.to_csv(f, header=activitySumExists, index=False)                                    #Writes the summary data to file
            
            #No idea why but outputting to CSV skips a line every fucking time
            fixWhiteSpaces(actSumPath, actSumPath2)

        
        #FOOD SUMMARY
        foodSumPath = os.path.join(os.getcwd(), 'data', 'SummaryData', 'FoodSummary.csv')
        foodSumPath2 = os.path.join(os.getcwd(), 'data', 'SummaryData', 'FoodSummary1.csv')

        if checkInputStatus(foodSumPath, date, 'Food'):
            foodStatsACT = auth2_client.foods_log(date=date['dashDate'])['summary']
            foodSumDF = pd.DataFrame({'Date':date['spreadDate'],
                                    'Calories':foodStatsACT['calories'],
                                    'Water':foodStatsACT['water'],
                                    'Carbs':foodStatsACT['carbs'],
                                    'Fat':foodStatsACT['fat'],
                                    'Fiber':foodStatsACT['fiber'],
                                    'Protein':foodStatsACT['protein'],
                                    'Sodium':foodStatsACT['sodium']}
                                    ,index=[0])
            
            with open(foodSumPath,'a') as f:
                tempFoodDF = pd.read_csv(foodSumPath)                                                     #Sets up file to be checked for header value
                foodSumExists = tempFoodDF.empty                                                     #Checks the file to see if it's empty
                foodSumDF.to_csv(f, header=foodSumExists, index=False)                                    #Writes the summary data to file
            
            #No idea why but outputting to CSV skips a line every fucking time
            fixWhiteSpaces(foodSumPath, foodSumPath2)

            print()
        
    print("Collection successful.")

        

#Takes the data from tokens.txt and gets the auth2_client needed by API
def getAuth2Client():
    
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
        
        print('\n-----Calling server for new tokens-----\n')
        server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
        server.browser_authorize()
        
        ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
        REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
        
        print('\n-----Writing new tokens to tokens.txt-----\n')
        
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
    
    return auth2_client


#Prints the last date that was synced using fitbit
def printLastSynced(dirList, printBool):

    #If no files in directory
    if len(dirList) == 0:
        print("No Previous App Calls \n")
        return
    
    #Convert files to two values in 2d array 
    for i in range(len(dirList)):
        fileMonth = dirList[i][4:6]
        fileDay = dirList[i][6:8]
        dirList[i] = [int(fileMonth), int(fileDay)]
    
    highDay = 0
    highMonth = 0

    #Loop to find the highest date in the file system
    for file in dirList:
        if file[0] > highMonth:
            highMonth = file[0]
            highDay = 1
        
        if file[1] > highDay:
            highDay = file[1]
    if printBool is True:
        print('Data synced up to : ' + str(highMonth) + '/' + str(highDay))

    return (str(highMonth) + str(highDay))

#Creates an array that is fed into the program to sync multiple dates at once
def getDateArray(lastCalledDate, userDate):
        
    monthDays = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
    
    dateArray.append(userDate)

    year = int(userDate[0:4])
    print(year)

    targetMonth = int(userDate[4:6])
    print(targetMonth)

    targetDay = int(userDate[6:])
    print(targetDay)

    prevMonth = int(lastCalledDate[0:2])
    print(prevMonth)

    prevDay = int(lastCalledDate[2:])
    print(prevDay)

    #Runs up until 1 day after 
    #Figure out how to increment and subsequently add the different dates to the array to be stored
    while targetMonth > prevMonth or targetDay > prevDay:

        prevDay = prevDay + 1

        #If the days have overflowed, it gets set to 1, and month is incremented
        if monthDays[prevMonth] < prevDay:
            prevDay = 1
            prevMonth = prevMonth + 1
            if prevMonth > 12:
                exit()

        if prevDay < 10:
            stringDay = '0' + str(prevDay)
        else stringDay = str(prevDay)

        if prevMonth < 10:
            stringMonth = '0' + str(prevMonth)
        else stringMonth = str(prevMonth)

        arrayElement = year + stringMonth + stringDay
        dateArray.append(arrayElement)
    return dateArray
    

#Creates all date formats needed by program, stores them in dictionary
def createDateFormats(userDate):
    #Gets ready to make date formats used by user
    month = userDate[4:6]
    monthInt = int(month)
    month2 = str(monthInt)
    
    day = userDate[6:]
    if day[0] == '0':                                                           #Takes out '01' to '1'
        day2 = day[1]
    else: 
        day2 = day
    
    year = userDate[0:4]
    
    #Three date formats needed by program
    userDate2 = year + '-' + month + '-' + day
    formalDate = month + '/' + day + '/' + year
    formalDateSpreadsheet = month2 + '/' + day2 + '/' + year

    date = {'inputDate'  : userDate,
            'dashDate'   : userDate2,
            'slashDate'  : formalDate,
            'spreadDate' : formalDateSpreadsheet}
    
    return date

#Takes a DF and writes it to the folder with the file name
def fixWhiteSpaces(inPath, outPath):
    
    with open(inPath) as input, open(outPath, 'w', newline='') as output:
        writer = csv.writer(output)
        for row in csv.reader(input):
            if any(field.strip() for field in row):
                writer.writerow(row)
    os.remove(inPath)
    time.sleep(.5)                                      #Guarantees that the file will not accidentally not exist
    os.rename(outPath, inPath)


#)@#(*$%)(@*#%)(@*&#%)(*@)(%) TEST
#Correctly formats and stores the Panda Dataframes given to the function, should only call API when the file doesn't exist, to save API calls
def intradayDataCollection(category, auth2_client, apiDate, detail, type, datatype, dateItem):
    timeList = []
    dataList = [] 

    fileName = dateItem + '_' + datatype + '.csv'
    basePath = os.path.join(os.getcwd(), 'data', datatype)
    fullPath = os.path.join(basePath, fileName)
    
    overwrite = False

    if not (os.path.isfile(fullPath)) or overwrite:
        StatsDict = auth2_client.intraday_time_series(category,                             #Calls intraday calories series, interval = 1min
                                                  base_date=apiDate, 
                                                  detail_level=detail)
        
        for i in StatsDict[type]['dataset']:
            dataList.append(i['value'])
            timeList.append(i['time'])
        df = pd.DataFrame({'Time' :timeList, datatype : dataList,})
            
        df.to_csv(fullPath, index=True, header=True)

    else: 
#Not Confirmed WORKING
        spaceLength = (25 - len(fileName))*' '                              #For spacing
        print(fileName + spaceLength + 'Already Exists, Skipping. . .')



#Takes a data structure and saves it to a csv
def writeToFile(df, name, folder, date, ind, head, overwrite):
    fileName = date + '_' + name + '.csv'
    basePath = os.path.join(os.getcwd(), 'data', folder)
    fullPath = os.path.join(basePath, fileName)
    
    if not (os.path.isfile(fullPath)) or overwrite:
        df.to_csv(fullPath, index=ind, header=head)
    else: 
#Not Confirmed WORKING
        spaceLength = (25 - len(fileName))*' '                              #For spacing
        print(fileName + spaceLength + 'Already Exists, Skipping. . .')


#Function to tell the user how long ago they submitted a token refresh
def timeLastCalled(current, lastCall):
    diff = int(current - lastCall)
    days = int(diff / (24 * 60 * 60))
    diff -= (days * 86400)
    hours = int(diff / (60 * 60))
    diff -= (hours * 3600)
    minutes = int(diff / 60)
    seconds = diff - (minutes * 60)
    
    
    print('\n-----------------------------------------------------------------------')
    print('Last call was: ' + str(days) + ' Day(s), ' + str(hours) + ' Hour(s), ' + str(minutes) + ' Minute(s), and ' + str(seconds) + ' Second(s) ago')
    trash = printLastSynced(os.listdir("data\\Heart\\"), True)
    print('No refresh needed, continuing to call: ' if (days == 0 and hours == 0 and minutes < 10) else 'Server call required')
    print('-----------------------------------------------------------------------')
    return None

#IN: Path to File, date['slashDate']
#OUT: False if data exists, True if not
def checkInputStatus(path, date, name):
    with open(path,'a') as f:
                
        tempDF = pd.read_csv(path)
        
        for i in tempDF['Date']:
            if type(i) == str and i == date['spreadDate']:
                firstPart = date['inputDate'] + '_' + name + 'Summary'
                spaceLength = (24 - len(firstPart))*' '
                print(firstPart + spaceLength  + ' Already Added,  Skipping. . .')
                return False
        
        return True
        
                    


#Main:
if __name__ == "__main__":
    main()