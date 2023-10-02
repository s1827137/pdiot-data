import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple
import matplotlib.ticker as ticker
import time
import datetime
import os
import shutil
import re

def extract_header_info(filename: str, header_size: int = 5) -> Tuple[str, str, int, str, str]:
    """
    :param filename: Path to recording file.
    :param header_size: The size of the header, defaults to 5.
    :returns: A 5-tuple containing the sensor type, activity type, activity subtype, subject id and any notes.
    """
    sensor_type = ""
    activity_type = ""
    activity_subtype = ""
    subject_id = ""
    notes = ""

    with open(filename) as f:
        head = [next(f).rstrip().split('# ')[1] for x in range(header_size)]
        for l in head:
            

            title, value = l.split(":")

            if title == "Sensor type":
                sensor_type = value.strip()
            elif title == "Activity type":
                activity_type = value.strip()
            elif title == "Activity subtype":
                activity_subtype = value.strip()
            elif title == "Subject id":
                subject_id = value.strip()
            elif title == "Notes":
                notes = value.strip()

    return sensor_type, activity_type, activity_subtype, subject_id, notes

def get_frequency(dataframe: pd.DataFrame, ts_column: str = 'timestamp') -> float:
    """
    :param dataframe: Dataframe containing sensor data. It needs to have a 'timestamp' column.
    :param ts_column: The name of the column containing the timestamps. Default is 'timestamp'.
    :returns: Frequency in Hz (samples per second)
    """

    return len(dataframe) / ((dataframe[ts_column].iloc[-1] - dataframe[ts_column].iloc[0]) / 1000)

def get_recording_length(dataframe: pd.DataFrame):
  """
  :param dataframe: Dataframe containing sensor data.
  """
  return len(dataframe) / get_frequency(dataframe)


# dir = "./out"
dir = input("Enter path to Processed/unprocessed CSV files: ")


checklist = [
    ['Respeck','Sitting', 'Normal'],
    ['Respeck','Standing','Normal'],
    ['Respeck','Lying down on left', 'Normal'],
    ['Respeck','Lying down right','Normal'],
    ['Respeck','Lying down back', 'Normal'],
    ['Respeck','Lying down on stomach','Normal'],
    ['Respeck', 'Normal walking', 'Normal'],
    ['Respeck', "Ascending stairs", 'Normal'],
    ['Respeck','Descending stairs','Normal'],
    ['Respeck', 'Shuffle walking', 'Normal'],
    ['Respeck', 'Running', 'Normal'],
    ['Respeck', 'Miscellaneous movements','Normal'],
    
    ['Thingy','Sitting', 'Normal'],
    ['Thingy','Standing','Normal'],
    ['Thingy','Lying down on left', 'Normal'],
    ['Thingy','Lying down right','Normal'],
    ['Thingy','Lying down back', 'Normal'],
    ['Thingy','Lying down on stomach','Normal'],
    ['Thingy', 'Normal walking', 'Normal'],
    ['Thingy', "Ascending stairs", 'Normal'],
    ['Thingy','Descending stairs','Normal'],
    ['Thingy', 'Shuffle walking', 'Normal'],
    ['Thingy', 'Running', 'Normal'],
    ['Thingy', 'Miscellaneous movements','Normal'],

    ['Respeck', 'Sitting', 'Coughing'],
    ['Respeck', 'Standing', 'Coughing'],
    ['Respeck', 'Lying down back','Coughing'],
    ['Respeck', 'Lying down right', 'Coughing'],
    ['Respeck', 'Lying down on left','Coughing'],
    ['Respeck','Lying down on stomach','Coughing'],
    ['Respeck','Sitting','Hyperventilating'],
    ['Respeck','Standing','Hyperventilating'],
    ['Respeck','Lying down back', 'Hyperventilating'],
    ['Respeck','Lying down right','Hyperventilating'],
    ['Respeck','Lying down on left','Hyperventilating'],
    ['Respeck','Lying down on stomach','Hyperventilating'],


    ['Respeck', 'Sitting', 'Talking'],
    ['Respeck','Sitting','Eating'],
    ['Respeck','Sitting','Singing'],
    ['Respeck','Sitting','Laughing'],
    ['Respeck','Standing','Talking'],
    ['Respeck','Standing', 'Eating'],
    ['Respeck','Standing','Singing'],
    ['Respeck','Standing','Laughing'],
    ['Respeck','Lying down back','Talking'],
    ['Respeck','Lying down back','Singing'],
    ['Respeck','Lying down back','Laughing'],
    ['Respeck','Lying down right','Talking'],
    ['Respeck','Lying down right','Singing'],
    ['Respeck','Lying down right','Laughing'],
    
    ['Respeck','Lying down on left','Talking'],
    ['Respeck','Lying down on left','Singing'],
    ['Respeck','Lying down on left','Laughing'],

    ['Respeck','Lying down on stomach','Talking'],
    ['Respeck','Lying down on stomach','Singing'],
    ['Respeck','Lying down on stomach','Laughing']

]
header_size = 5
def getDataFrame(filename):
    file = os.path.join(dir, filename)
    filename_raw = filename.split("/")[-1].split(".")[0]
    try:
            sensor_type, activity_type, activity_subtype, subject_id, notes = extract_header_info(filename=file)
            df = pd.read_csv(file, header=header_size)
            df['sensor_type'] = sensor_type
            df['activity_type'] = activity_type
            df['activity_subtype'] = activity_subtype
            df['subject_id'] = subject_id
            df['notes'] = notes
            df['recording_id'] = filename_raw
            df['formatTime'] =  datetime.datetime.fromtimestamp(df.timestamp.iat[-1] / 1000).strftime('%Y-%m-%d_%H-%M-%S')
    except:
        # print('Error reading file header... Skipping file')
        df = pd.read_csv(file)

    
    
    return df
def parseFileName(filename):
    frags = filename.split('_')
    if(len(frags) > 5):
        # Device, uid,task,subtask, cleanstatus
        return [frags[0], frags[1], frags[2],frags[3],frags[4]]
    else:
        print("Error Invalid File name " + str(filename))
def validate():
    filenames = os.listdir(dir)
    filenames =[filename for filename in filenames if filename.lower().endswith(".csv")]
    checkFileNames(filenames)
    checkCorrectNumFiles(filenames)
    checkExtraActivities(filenames)
    checkMissingActivities(filenames)
    checkFrequency(filenames)
    checkLength(filenames)
    checkDuplicateActivities(filenames)
    checkSingleUID(filenames)
    checkCleanUnprocessedPairs(filenames)
    # for filename in filenames:
    #     pass



def checkCorrectNumFiles(filenames):
    print("Checking File Count.")
    count = 0
    for name in filenames:
        if name.lower().endswith(".csv"):
            count +=1
    
    if(count != 56*2):
        print(f'\t Invalid Number of Files Detected {count}, Expected {56*2}')


def checkFileNames(filenames):
    # invalidFiles = []
    print("Checking File Names:")
    pattern = r'^(Thingy|Respeck)_s\d+_[a-zA-Z ]+_[a-zA-Z]+_(unprocessed|clean)_[0-9]{2}-[0-9]{2}-[0-9]{4}_[0-9]{2}-[0-9]{2}-[0-9]{2}\.csv$'
    for name in filenames:
        if not re.match(pattern, name):
            print(f'\tFile Found with Incorrect Naming Scheme: {name}')
def checkFrequency(filenames): # TODO Check/compare results without timestamps using avg time between records
    print("Checking Frequency:")
    for name in filenames:
        df= getDataFrame(name)
        feq = get_frequency(df)
        if feq < 24 or feq > 26:
            print(f'\t Invalid Frequency Detected: {feq} For: {name}')
def checkLength(filenames): # TODO Check/compare results without timestamps using hardcoded 25hz to compare
    print("Checking Length:")
    for name in filenames:
        data = parseFileName(name)
        if(data[4] == "clean"):
            df= getDataFrame(name)
            length = get_recording_length(df)
            if length < 28 or length > 32:
                print(f'\t Invalid Length Detected: {length} For: {name}')
def checkExtraActivities(filenames):
    print("Checking for Extra Activities")
    for name in filenames:
        data = parseFileName(name)
        found = False
        for item in checklist:
            if item[0] == data[0] and item[1] == data[2]  and item[2] == data[3]: # Device name,Activity,subtype
                found = True
                break
        if not found:
            print(f'\t Unknown Activity Detected: {name}')
def checkMissingActivities(filenames):
    print("Checking for Missing Activities")
    for item in checklist:
        found = False
        for name in filenames:
            data = parseFileName(name)
            if item[0] == data[0] and item[1] == data[2]  and item[2] == data[3]: # Device name,Activity,subtype
                found = True
                break
        if not found:
            print(f'\tActivity Missing: {item}' )          
def checkDuplicateActivities(filenames):
    print("Checking for Duplicate Activities")
    for item in checklist:
        found = []
        for name in filenames:
            data = parseFileName(name)
            if item[0] == data[0] and item[1] == data[2]  and item[2] == data[3] and data[4] == 'clean': # Device name,Activity,subtype
                found.append(name)
                # break
        if(len(found)> 1):
            print(f'\t Duplicate Activies Found: {found}')
def checkSingleUID(filenames):
    print("Checking for Single StudentID")
    ids = set()
    for name in filenames:
        data = parseFileName(name)
        ids.add(data[1])
    if len(ids) > 1:
        print(f'\tMore than one Student ID Detected Review files for Typo\'s:  {ids}')
def checkCleanUnprocessedPairs(filename):
    print("Checking for Pairs of Processed/Unprocessed Files:")
    for name1 in filename:
        data1 = parseFileName(name1)
        tmp = ""
        if data1[4] == "clean":
            tmp = name1.replace("clean","unprocessed")
        else:
            tmp = name1.replace("unprocessed","clean")
        found = False
        for name2 in filename:
            if(name2 == tmp):
                found = True
                break
        if not found:
            print(f'\tCleaned/Unprocessed file Pair Missing for File: {name1}')
def checkThingyOrintation(filenames): #TODO 
    # Standing -x
    # Back +z
    # belly -z
    pass
def checkRespeckOrintation(filenames): #TODO
    # Standing -y
    # Laying Right +x and +z
    # Laying Left -x and -z
    # back + z
    # belly -z
    pass
def checkDuplicateTimeStamps(filenames): #TODO
    pass

validate()