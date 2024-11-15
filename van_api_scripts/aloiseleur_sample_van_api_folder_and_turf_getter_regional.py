# standard imports
import pandas as pd

# utility imports
from datetime import datetime, timedelta
import pytz
import re
import os

# imports for making API requests and parsing JSON responses
import requests
import json

# imports for using Google Service Acct to access Drive/Sheets
import pygsheets
from google.oauth2 import service_account


#########################################################
# SETTING VARIABLES FOR DATE, CREDENTIALS, BASE API URL #
#########################################################

# today's date
current_date = datetime.now(pytz.timezone('America/New_York')).strftime("%Y-%m-%d")
current_timestamp = datetime.now(pytz.timezone('America/New_York')).strftime("%Y-%m-%d - %H:%M:%S")
yesterdays_date = (datetime.now(pytz.timezone('America/New_York')) - timedelta(days=1)).strftime("%Y-%m-%d")

# Setting API credentials via Environmental Variables
print(f"Script starting at: {current_timestamp}") 
print("Getting VAN API credentials from environment variable")
secrets = json.loads(os.environ["VAN_API_CREDS"])

APPLICATION_NAME = secrets["van_api"]["APPLICATION_NAME"]
API_KEY = secrets["van_api"]["API_KEY"]

# auth variable to feed to request's .get() method
van_auth = (APPLICATION_NAME, API_KEY + "|0")

# URL variable; also fed to the request's .get() method
BASE_URL = "https://api.securevan.com/v4"


###############
# GET FOLDERS #
###############

# specific API endpoint we want to query; also fed to the request's .get() method
endpoint = "/folders"

# storing API's "answers" to our request to a variable called response
print("Getting initial response from VAN API: first page of folders")
response = requests.get(BASE_URL + endpoint, auth=van_auth)
print(f"API response status: {response}")

# taking the response and cleaning it up for parsing; storing in the variable output
output = json.loads(response.text)

# empty list to store folder details received from API
folders = []

# count variable for how many folder records we're getting back
count = output["count"]
print(f"Num of folders in response (pre-filtering): {count}")

# store folder records in API's initial response to folders list
hc_folder_list = [
    "!! GOTV_R01_Turf"  # add additional folders as needed
]
print(f"Folders we'll be looking for: {hc_folder_list}" )

try:
    for folder in output["items"]:
        f_name = folder["name"]

        if f_name in hc_folder_list:
            print(f"Adding folder: {f_name}")
            folders.append(folder)

    # store first of what may be many pages of results
    next_link = output["nextPageLink"]

    # loop through remaining pages, adding folder details to folders,
    # then proceed thru additional pages to net more
    if next_link != None:
        for page in range((count//10) + 1):
            print(f"On page {page} of Folder results")
            print(f"Next Link: {next_link}")

            if next_link != None:
                sub_response = requests.get(next_link, auth=van_auth)

                sub_output = json.loads(sub_response.text)

                for folder in sub_output["items"]:
                    f_name = folder["name"]

                    if f_name in hc_folder_list:
                        print(f"Adding folder: {f_name}")
                        folders.append(folder)

                    next_link = sub_output["nextPageLink"]
            else:
                print("No more Folder pages to loop through!")
                break
    else:
        print("No Folder pages to loop through!")
except Exception as e:
    print(f"An error occurred while getting folder data: {type(e).__name__}, {str(e)}")

# store folder JSONs in a Pandas DataFrame
print("Storing folder JSONs in a Pandas DF")
df_folders = pd.DataFrame.from_dict(folders)

print(f"df_folders info: {df_folders.info()}")


#########################
# GET TURF LIST NUMBERS #
#########################

# specific API endpoint we want to query; also fed to the request's .get() method
endpoint = "/printedLists"

# pull turf packet IDs generated yesterday; can be altered w/date format as str: "YYYY-MM-DD"
date = yesterdays_date

print("Folders retrieval complete; now retrieving turf lists numbers")

# establish empty list to store turf packet information
turfs = []

# parameters to feed the API (so it knows what to respond with)
try:
    for x in range(len(df_folders)):
        params = {
            "generatedAfter": date
            , "folderName": df_folders["name"][x]
        }

        print(f"Params for turf to be retrieved: {params['generatedAfter']}, {params['folderName']}")

        # storing API's "answers" to our request to a variable called response
        response = requests.get(BASE_URL + endpoint, params=params, auth=van_auth)
        print(f"API response status: {response}")

        # taking the response and cleaning it up for parsing; storing in the variable output
        output = json.loads(response.text)

        # count variable for how many turf packet records we're getting back
        count = output["count"]
        remaining = count
        print(f"Num of turfs in response: {count}")

        # store turf packet records in API's initial response to turfs list
        for item in output["items"]:
            remaining -= 1
            print(f"Turf: {item['name']}, Remaining turfs: {remaining}")
            turfs.append(item)

        # store first of what may be many pages of results
        next_link = output["nextPageLink"]

        # loop through remaining pages, adding turf packets to turfs, then proceed 
        # thru additional pages to net more
        if next_link != None:
            for page in range((count//10) + 1):
                print(f"Page: {page}")
                print(f"Next Link: {next_link}")

                if next_link != None:
                    sub_response = requests.get(next_link, auth=van_auth)

                    sub_output = json.loads(sub_response.text)

                    for item in sub_output["items"]:
                        turfs.append(item)
                        remaining -= 1
                        print(f"(Sub) Turf: {item['name']}, Remaining turfs: {remaining}")
                        next_link = sub_output["nextPageLink"]
                else:
                    print("No more pages to loop through!")
                    break
        else:
            print("No pages to loop through!")
except Exception as e:
    print(f"An error occurred while getting turf packet data: {type(e).__name__}, {str(e)}")

# store turf packet JSONs into their own Pandas DataFrame
print("Storing turf packet JSONs in a Pandas DF")
df_turfs = pd.DataFrame.from_dict(turfs)

print(f"df_turfs info: {df_turfs.info()}")


######################################################
# GET FOLDER METADATA (DOOR COUNT, LIST COUNT, ETC.) #
######################################################

print("Turf packet retrieval complete; now grabbing Turf Folder Metadata")

# specific API endpoint we want to query; also fed to the request's .get() method
endpoint = "/savedLists"

# establish empty list to store folder metadata
folder_meta = []

# get folderIDs from the folder DF (to feed the API as params)
folder_ids = df_folders["folderId"].unique()

# parameters to feed the API (so it knows what to respond with)
try:
    for x in range(len(folder_ids)):
        params = {
            "folderId": folder_ids[x]
        }

        # storing API's "answers" to our request to a variable called response
        response = requests.get(BASE_URL + endpoint, params=params, auth=van_auth)

        # taking the response and cleaning it up for parsing; storing in the variable output
        output = json.loads(response.text)

        # count variable for how many turf packet records we're getting back
        count = output["count"]
        remaining = count

        # store turf packet records in API's initial response to turfs list
        for item in output["items"]:
            folder_meta.append(item)
            remaining -= 1
            print(f"Folder: {item['name']}, Remaining folders: {remaining}")

        # store first of what may be many pages of results
        next_link = output["nextPageLink"]

        # loop through remaining pages, adding turf packets to turfs, then proceed thru additional pages to net more
        if next_link != None:
            for page in range((count//10) + 1):
                print(f"Page: {page}")
                print(f"Next Link: {next_link}")

                if next_link != None:
                    sub_response = requests.get(next_link, auth=van_auth)

                    sub_output = json.loads(sub_response.text)

                    for item in sub_output["items"]:
                        folder_meta.append(item)
                        remaining -= 1
                        print(f"Folder: {item['name']}, Remaining folders: {remaining}")
                        next_link = sub_output["nextPageLink"]
                else:
                    print("No more pages to loop through!")
                    break
        else:
            print("No pages to loop through!")
except Exception as e:
    print(f"An error occurred while getting turf packet data: {type(e).__name__}, {str(e)}")

# store folder metadata JSONs in their own Pandas DataFrame
print("Storing folder metadata JSONs in a Pandas DF")
df_folder_meta = pd.DataFrame.from_dict(folder_meta)

print(f"df_folder_meta info: {df_folder_meta.info()}")


######################################################
# SEND FOLDERS AND TURFS DATAFRAMES TO GOOGLE SHEETS #
######################################################

print("Folder metadata retrieved; now sending turf, folder, and metadata to Google Sheets")

# Authorize pygsheets
# use custom credentials object to read from the secrets dict
SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
)

SERVICE_ACCOUNT_CREDS = secrets["google_service_account"]

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_CREDS, scopes=SCOPES
)
gc = pygsheets.authorize(custom_credentials=credentials)
packetland_turf_list_number_tracker = "https://docs.google.com/spreadsheets/d/[REDACTED]"
sh = gc.open_by_url(packetland_turf_list_number_tracker)
folders_sheet = sh.worksheet_by_title("gotv_import_folders")
turfs_sheet = sh.worksheet_by_title("gotv_import_turfs")
folder_meta_sheet = sh.worksheet_by_title("gotv_import_folder_meta")

# rename dataframe columns before writing them to the Google Sheet
df_folders.rename(columns={"folderId": "folder_id"
                           , "name": "folder_name"
                           }
                  , inplace=True
                  )
df_turfs.rename(columns={"number": "turf_list_number"
                         , "name": "turf_list_name"
                         , "eventSignups": "event_signups"
                         , "listSize": "list_size"
                         }
                , inplace=True
                )
df_folder_meta.rename(columns={"description": "description"
                               , "listCount": "list_count"
                               , "doorCount": "door_count"
                               , "isSuppressed": "is_suppressed"
                               , "savedListId": "saved_list_id"
                               , "name": "turf_folder_name"
                               }
                      , inplace=True
                      )

# clear sheets to prepare for import, then import
print("Clearing import tabs on Google Sheet to import updated data")
folders_sheet.clear()
folders_sheet.set_dataframe(
    df=df_folders
    , start="A1"
    , copy_index=False
    , copy_head=True
    , escape_formulae=False
)

turfs_sheet.clear()
turfs_sheet.set_dataframe(
    df=df_turfs
    , start="A1"
    , copy_index=False
    , copy_head=True
    , escape_formulae=False
)

folder_meta_sheet.clear()
folder_meta_sheet.set_dataframe(
    df=df_folder_meta
    , start="A1"
    , copy_index=False
    , copy_head=True
    , escape_forumale=False
)

# current timestamp
current_timestamp = datetime.now(pytz.timezone('America/New_York')).strftime("%Y-%m-%d - %H:%M:%S")

# add update timestamps
folders_sheet.update_value("D1", "UPDATED AT:")
folders_sheet.update_value("E1", current_timestamp)
turfs_sheet.update_value("I1", "UPDATED AT:")
turfs_sheet.update_value("J1", current_timestamp)
folder_meta_sheet.update_value("H1", "UPDATED AT:")
folder_meta_sheet.update_value("I1", current_timestamp)

print("Google Sheets updated!")
