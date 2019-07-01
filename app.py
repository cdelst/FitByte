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


#Import all the packages that I probably don't need
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
    
    #Creates the array that is fed into the program for sync
    dateArray = getDateArray(lastCalledDate, userDate)


    #Loops through all dates from lastSynced to current user input
    for dateItem in dateArray:
        
        print("Calling Date: " + dateItem)
        
        #Creates a dictionary of all the different date formats used in this API, see f()
        date = createDateFormats(dateItem)

        #Collects heartrate data by the second
        intradayDataCollection('activities/heart',
                                auth2_client,
                                date['dashDate'], 
                                '1sec', 
                                'activities-heart-intraday',
                                'Heart',
                                dateItem)
        
        #Collects distance data by the minute
        intradayDataCollection('activities/distance',
                                auth2_client,
                                date['dashDate'],                            
                                '1min',                             
                                'activities-distance-intraday',
                                'Distance',
                                dateItem)
        
        #Collects step data by the minute
        intradayDataCollection('activities/steps',  
                                auth2_client,                              
                                date['dashDate'], 
                                '1min',
                                'activities-steps-intraday',
                                'Steps',
                                dateItem)
        
        #Collects elevation data by the minute
        intradayDataCollection('activities/elevation', 
                                auth2_client,
                                date['dashDate'], 
                                '1min',
                                'activities-elevation-intraday',
                                'Elevation',
                                dateItem)
        
        #Collects calories data by the minute
        intradayDataCollection('activities/calories', 
                                auth2_client,
                                date['dashDate'], 
                                '1min',
                                'activities-calories-intraday',
                                'Calories',
                                dateItem)
        
        #Gets the sleep data from the api
        fit_statsSLE = auth2_client.sleep(date=date['dashDate'])
       
        #Initialize lists used
        stime_list = []
        sval_list = []

        #Parse data
        for i in fit_statsSLE['sleep'][0]['minuteData']:
            stime_list.append(i['dateTime'])
            sval_list.append(i['value'])

        #Creates a data frame from the parsed dictionary
        sleepDF = pd.DataFrame({'Time':stime_list, 
                                'State':sval_list})
        
        #Casts the state from one of the three options 
        sleepDF['Interpreted'] = sleepDF['State'].map({'2':'Awake', 
                                                    '3':'Very Awake', 
                                                    '1':'Asleep'})
        
        #Create a CSV file and save to it
        writeToFile(sleepDF, 'Sleep', 'Sleep', dateItem, True, True, False)


        #SLEEP SUMMARY
        #Gets the local path of my sleep csv file
        sleepSumPath = os.path.join(os.getcwd(), 'data','SummaryData', 'SleepSummary.csv')
        sleepSumPath2 = os.path.join(os.getcwd(), 'data', 'SummaryData', 'SleepSummary1.csv')
        
        #Checks if date has already been inputted
        if checkInputStatus(sleepSumPath, date, 'Sleep'):
            #If not, get the summary statistics from the api
            fit_statsSum = auth2_client.sleep(date=date['dashDate'])['sleep'][0]
            
            #Create a data frame from the contents of the api call
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
        
            #Open the sleep summary csv file
            with open(sleepSumPath,'a') as f:

                #Create a dataframe from that CSV
                tempSleepDF = pd.read_csv(sleepSumPath)                                                     #Sets up file to be checked for header value
                
                #Does it exist?
                sleepSumExists = tempSleepDF.empty                                                          #Checks the file to see if it's empty
                
                #Concat the previous lines with the new one.  Add header if there was no previous file
                ssummarydf.to_csv(f, header=sleepSumExists, index=False)                                    #Writes the summary data to file
            
            #No idea why but outputting to CSV skips a line every time, this fixes that.  See f()
            fixWhiteSpaces(sleepSumPath, sleepSumPath2)
        

        #ACTIVITY SUMMARY
        #Get the relative paths to the activity summary file
        actSumPath = os.path.join(os.getcwd(), 'data', 'SummaryData', 'ActivitySummary.csv')
        actSumPath2 = os.path.join(os.getcwd(), 'data', 'SummaryData', 'ActivitySummary1.csv')

        #See checkInputStatus()
        if checkInputStatus(actSumPath, date, 'Activity'):
            
            #Calls the api for the activity summary
            sumFitStatsACT = auth2_client.activities(date=date['dashDate'])['summary']
            
            #Parses the api call into a dataframe
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
            
            #Open the location of the previous summary file
            with open(actSumPath,'a') as f:
                
                #See if it exists
                tempActivityDF = pd.read_csv(actSumPath)                                                     
                activitySumExists = tempActivityDF.empty                                                     
                
                #Concat old file and new file
                actSumDF.to_csv(f, header=activitySumExists, index=False)                                    
            
            #No idea why but outputting to CSV skips a line every time.  This fixes that
            fixWhiteSpaces(actSumPath, actSumPath2)

        
        #FOOD SUMMARY
        #See explanation on the previous two summary functions, they are exactly similar
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
                tempFoodDF = pd.read_csv(foodSumPath)                                                    
                foodSumExists = tempFoodDF.empty                                                     
                foodSumDF.to_csv(f, header=foodSumExists, index=False)                                    
            
            
            fixWhiteSpaces(foodSumPath, foodSumPath2)

            print()
        
    print("Collection successful.")


#Takes the data from tokens.txt and gets the auth2_client needed by API
def getAuth2Client():
    
    #Open the tokens.txt file as f
    with open('tokens.txt') as f:

        #Make an array out of the different lines of the file
        content = f.readlines()

    #Clean the array values so that they work
    content = [x.strip() for x in content]

    #Sets up the date-time to check if a new api call is required
    dt = int(time.time())
    lastdt = int(content[2])
    expireTime = 10 * 60  #(10 min in UNIX time)

    #User specific data, read from line 1 and 2 of tokens file
    CLIENT_ID = content[0]
    CLIENT_SECRET = content[1]

    #Print Days, Hours, Minutes, Seconds since last server refresh, see timeLastCalled()
    timeLastCalled(dt, lastdt)

    #Determine if a new server call is required to refresh tokens
    if((dt - lastdt) >= expireTime): #(If time last called was greater than 10 minutes ago)
        
        print('\n-----Calling server for new tokens-----\n')
        
        #Refreshses tokens
        server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
        server.browser_authorize()
        
        #Retrieves new tokens from FitBit
        ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
        REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
        
        print('\n-----Writing new tokens to tokens.txt-----\n')
        
        #Writes updated information to tokens.txt for next run of program
        with open('tokens.txt', 'w') as f:                                                              
            f.write(str(CLIENT_ID) + '\n')
            f.write(str(CLIENT_SECRET) + '\n')
            f.write(str(dt) + '\n') #(Current Unix Time)
            f.write(str(ACCESS_TOKEN) + '\n')
            f.write(str(REFRESH_TOKEN) + '\n')
    
    else: #(If a server call was not required, take previously acquired tokens)                                                                                               
        ACCESS_TOKEN = content[3]
        REFRESH_TOKEN = content[4]

    #Use those tokens and ID's to make the auth2_client that will be used for API calls
    auth2_client = fitbit.Fitbit(CLIENT_ID,                                                             
                                CLIENT_SECRET, 
                                oauth2=True, 
                                access_token=ACCESS_TOKEN, 
                                refresh_token=REFRESH_TOKEN)
    
    #Return the client
    return auth2_client


#Prints the last date that was synced using fitbit
def printLastSynced(dirList, printBool):

    #If no files in directory
    if len(dirList) == 0:
        print("No Previous App Calls \n")
        return
    
    #Convert files to two values in 2d array 
    for i in range(len(dirList)):

        #Pulls the month from the filename
        fileMonth = dirList[i][4:6]
        
        #Pulls the day from the filename
        fileDay = dirList[i][6:8]
        
        #Make a combo and save them into dirList
        dirList[i] = [int(fileMonth), int(fileDay)]
    
    highDay = 0
    highMonth = 0

    #Loop to find the highest date in the file system
    for file in dirList:
        
        #if the month is greater than previous, set the month to new value, reset days
        if file[0] > highMonth:
            highMonth = file[0]
            highDay = 1
        
        #If the day is greater than previous, set the day to new value
        if file[1] > highDay:
            highDay = file[1]
    
    #If print was specified in function call, print
    if printBool is True:
        print('Data synced up to : ' + str(highMonth) + '/' + str(highDay))

    #Return the date of the most recent call, signified by high month/day
    return (str(highMonth) + str(highDay))

#Creates an array that is fed into the program to sync multiple dates at once
def getDateArray(lastCalledDate, userDate):
        
    #Initialize the days in each month for future use
    monthDays = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
    
    #Stores first user inputted date
    dateArray.append(userDate)

    #Gets year from user input
    year = int(userDate[0:4])
    print(year)

    #Gets month from user
    targetMonth = int(userDate[4:6])
    print(targetMonth)

    #Gets day from user
    targetDay = int(userDate[6:])
    print(targetDay)

    #Gets month from last call made
    prevMonth = int(lastCalledDate[0:2])
    print(prevMonth)

    #Gets day from last call made
    prevDay = int(lastCalledDate[2:])
    print(prevDay)

    #Runs up until 1 day after 
    #Figure out how to increment and subsequently add the different dates to the array to be stored
    while targetMonth > prevMonth or targetDay > prevDay:

        #Increment day
        prevDay = prevDay + 1

        #If the days have overflowed, it gets set to 1, and month is incremented
        if monthDays[prevMonth] < prevDay:
            prevDay = 1
            prevMonth = prevMonth + 1

            #Error if a new year is entered for now
            if prevMonth > 12:
                exit()

        #If day value is <10, add a '0' in front of it
        if prevDay < 10:
            stringDay = '0' + str(prevDay)
        else stringDay = str(prevDay)

        #If month value is <10, add a '0' in front of it
        if prevMonth < 10:
            stringMonth = '0' + str(prevMonth)
        else stringMonth = str(prevMonth)

        #Create the new array element
        arrayElement = year + stringMonth + stringDay
        
        #Add that new element to the end of the array
        dateArray.append(arrayElement)
    
    #Return that filled date array
    return dateArray
    

#Creates all date formats needed by program, stores them in dictionary
def createDateFormats(userDate):
    
    #Gets ready to make date formats used by user
    year = userDate[0:4]
    month = userDate[4:6]
    monthInt = int(month)
    month2 = str(monthInt)
    day = userDate[6:]

    #If the leading character is a 0, take it out
    if day[0] == '0':                                                           
        day2 = day[1]
    else: 
        day2 = day
    
    #Three date formats needed by program
    userDate2 = year + '-' + month + '-' + day
    formalDate = month + '/' + day + '/' + year
    formalDateSpreadsheet = month2 + '/' + day2 + '/' + year

    #Create a dictionary full of all of the different date formats
    date = {'inputDate'  : userDate,
            'dashDate'   : userDate2,
            'slashDate'  : formalDate,
            'spreadDate' : formalDateSpreadsheet}
    
    #Returns that dictionary just made
    return date

#Takes a DF and writes it to the folder with the file name
def fixWhiteSpaces(inPath, outPath):
    
    #Open the inPath as input, and the outPath as the output
    with open(inPath) as input, open(outPath, 'w', newline='') as output:
        
        #Initialize csv writer
        writer = csv.writer(output)
       
        #Loops through every row in the file
        for row in csv.reader(input):

            #If the row exists in the input file, write it to the output file
            if any(field.strip() for field in row):
                writer.writerow(row)
    
    #Delete the old file
    os.remove(inPath)
    
    #Wait 500 ms because windows likes getting itself confused and saying the file doesn't exist
    time.sleep(.5)                                      
    
    #Make the outPath look exactly like the old inPath, effectively replacing it
    os.rename(outPath, inPath)


#Correctly formats and stores the Panda Dataframes given to the function, should only call API when the file doesn't exist, to save API calls
def intradayDataCollection(category, auth2_client, apiDate, detail, dtype, datatype, dateItem):
    timeList = []
    dataList = [] 

    #Creates a filename and paths from values inputted to function
    fileName = dateItem + '_' + datatype + '.csv'
    basePath = os.path.join(os.getcwd(), 'data', datatype)
    fullPath = os.path.join(basePath, fileName)
    
    #Custom value if you want to rewrite a file that already exists for any reason, used to fix a large amount of errors
    overwrite = False

    #If the file doesn't exist, or overwrite is on, execute if
    if not (os.path.isfile(fullPath)) or overwrite:
        
        #Make an API call with the inputted values from function call
        StatsDict = auth2_client.intraday_time_series(category,                             #Calls intraday calories series, interval = 1min
                                                  base_date=apiDate, 
                                                  detail_level=detail)
        
        #Parses the dictionary
        for i in StatsDict[dtype]['dataset']:
            dataList.append(i['value'])
            timeList.append(i['time'])
        
        #Creates a dataframe from the parsed data
        df = pd.DataFrame({'Time' :timeList, datatype : dataList,})
        
        #Writes the data to a file
        df.to_csv(fullPath, index=True, header=True)

    else: 
        
        #Output a message that the file already exists
        spaceLength = (25 - len(fileName))*' '                              #For spacing
        print(fileName + spaceLength + 'Already Exists, Skipping. . .')


#May be redundant? 
#Takes a data structure and saves it to a csv
def writeToFile(df, name, folder, date, ind, head, overwrite):
    
    #Creates necessary variable like path and name for the writing
    fileName = date + '_' + name + '.csv'
    basePath = os.path.join(os.getcwd(), 'data', folder)
    fullPath = os.path.join(basePath, fileName)
    
    #If the file doesn't exist, or overwrite is on 
    if not (os.path.isfile(fullPath)) or overwrite:
        df.to_csv(fullPath, index=ind, header=head)
    else: 
        
        #Prints a message that the file already exists
        spaceLength = (25 - len(fileName))*' '                              #For spacing
        print(fileName + spaceLength + 'Already Exists, Skipping. . .')


#Function to tell the user how long ago they submitted a token refresh
def timeLastCalled(current, lastCall):
    
    #Calculates the difference between the two calls
    diff = int(current - lastCall)

    #Converts to days by dividing by (hours in a day * minutes in an hour * seconds in a minute)
    days = int(diff / (24 * 60 * 60))

    #Subtract the value of days from the total difference
    diff -= (days * 86400)

    #Gets hours from remaining time by multiplying minutes/hour and seconds/minute
    hours = int(diff / (60 * 60))

    #Subtracts that value from the difference
    diff -= (hours * 3600)

    #Gets minutes by simply dividing by remaining seconds
    minutes = int(diff / 60)

    #Should result in 0
    seconds = diff - (minutes * 60)
    
    #Print the results of the previous calculations
    print('\n-----------------------------------------------------------------------')
    print('Last call was: ' + str(days) + ' Day(s), ' + str(hours) + ' Hour(s), ' + str(minutes) + ' Minute(s), and ' + str(seconds) + ' Second(s) ago')
   
    #Checks random file to see if it exists
    trash = printLastSynced(os.listdir("data\\Heart\\"), True)
    
    print('No refresh needed, continuing to call: ' if (days == 0 and hours == 0 and minutes < 10) else 'Server call required')
    print('-----------------------------------------------------------------------')
    return None

#IN: Path to File, date['slashDate']
#OUT: False if data exists, True if not
def checkInputStatus(path, date, name):
    
    #Open the file described in function call
    with open(path,'a') as f:

        #Create a data frame from that file
        tempDF = pd.read_csv(path)
        
        #For the duration of the file
        for i in tempDF['Date']:

            #If the file already exists, say so, if not, do nothing
            if type(i) == str and i == date['spreadDate']:
                firstPart = date['inputDate'] + '_' + name + 'Summary'
                spaceLength = (24 - len(firstPart))*' '
                print(firstPart + spaceLength  + ' Already Added,  Skipping. . .')
                return False
        
        #Not sure why I'm returning true
        return True
        
#Main:
#I honestly still have no idea why you have to add this
if __name__ == "__main__":
    main()