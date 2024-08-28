# This python file helps remove multiple endpoints from its current group by interacting with Sophos Central API.
# Here you need to provide the following when running the script:
# 1. Absolute path of the .csv file containing the System IDs of the target machines.
# 2. API Client ID generated from the Sophos Central Console
# 3. API Client Secret generated from the Sophos Central Console
#
# When the script is executed, it will also write a log file in a form of .csv file for easier checking.


# Algorigthm steps
# Present the menu and execute necessary function based on customer's option.
# 1. Get the .csv file
#   1.1 validate the contents of .csv file and ask the user if it's the right file.
#   1.2 if not the right file, ask the user again for the right file.
#

import os
import sys
import time
from datetime import datetime
import csv
import json
import requests



# Generate current timestamp when the script is run and generate log file in .csv format
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
logFileName = f"{timestamp}_log.csv"

# Define headers of .csv log file
logFileheaders = ['System_ID', 'Hostname', 'Group_ID', 'GroupName', 'RemovalStatus']


# Get Sophos Central Token Function using API credentials
def get_token(client_id, client_secret):
    token = ""
    url = "https://id.sophos.com/api/v2/oauth2/token"
    payload = 'grant_type=client_credentials&client_id='+client_id+'&client_secret='+client_secret+'&scope=token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer null'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    token_response = json.loads(response.text)

    if ('errorCode' in token_response):
        if (token_response['errorCode'] != "success"):
            print("\n\nUnable to retrieve Sophos Central token, please check provided API ID and Secret.")
        elif(token_response['errorCode'] == "success"):
            token = token_response["access_token"]
        else:
            print("\n\nAn issue was encountered with API request.")
            input("Press Enter key to continue...")

    return token;

# Function to get tenant
def get_tenant(token):
    url = "https://api.central.sophos.com/whoami/v1"

    payload={}
    headers = {
      'Authorization': 'Bearer ' + token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    
    tenant = json.loads(response.text)
    tenant_id = tenant["id"]
    tenant_region = tenant["apiHosts"]["dataRegion"]
    
    print("\n\nSuccess! The Tenant ID is: " + f'{tenant_id}' + "\n")
    
    return [tenant_id,tenant_region];

# Function to get all groups
def get_all_groups(token, tenantRegion, tenantID):
    url = f"{tenantRegion}/endpoint/v1/endpoint-groups?pageSize=1000"
    headers = {
        'Authorization': f'Bearer {token}',
        'X-Tenant-ID': tenantID,
        'Content-Type': 'application/json'
    }
    all_groups = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        all_groups.extend(data['items'])
        url = data.get('next') # Attempt to get the next page URL if possible
    return all_groups;

# Function to get group id based on group name
def find_group_id_by_name(allGroups, groupName):
    for group in allGroups:
        if group['name'].lower() == groupName.lower():
            return group['id']
    return None;

# Function to remove endpoint from group
def remove_agent_from_group(token, tenantRegion, tenantID, systemid, groupID):

    url = tenantRegion+"/endpoint/v1/endpoint-groups/"+groupID+"/endpoints/"+systemid
    headers = {
        'Authorization': 'Bearer '+token,
        'X-Tenant-ID': tenantID
    }

    response2 = requests.delete(url, headers=headers)

    if response2.status_code == 200:
        print("Successfully removed endpoint from group")
        response2.status_code = f"{response2.status_code}: Successfully removed endpoint from group."
    else:
        print(f"Failed to remove agent. Status code: {response2.status_code}")
        print(f"Response: {response2.text}")
        print(url)

    return [response2.status_code, url];


os.system('cls')
print("")
print("This python file helps remove multiple endpoints from its current group by interacting with Sophos Central API.")
print("Here you need to provide the following when running the script:")
print("1. Absolute path of the .csv file containing the System IDs of the target machines.")
print("2. API Client ID generated from the Sophos Central Console")
print("3. API Client Secret generated from the Sophos Central Console")
print("")
print("When the script is executed, it will also write a log file in a form of <timestamp>_log.csv file for easier checking.")
print("-----------------------------------------------------------------------------------------------------------------\n")
csvFilePath = input("Enter .csv full file path: ")
clientID = input("Enter API Client ID: ")
clientSecret = input("Enter API Client Secret: ")
print("-----------------------------------------------------------------------------------------------------------------\n")

print(f"Input .csv file path: {csvFilePath}")
print(f"API Client ID: {clientID}")
print(f"API Client Secret: {clientSecret}")
print("-----------------------------------------------------------------------------------------------------------------\n")

print(f"Checking provided {csvFilePath} file...")
if os.path.exists(csvFilePath):
    #try:
        with open(csvFilePath, mode='r') as file:
            csv_reader = csv.DictReader(file)

            # Check if the required columns exists (first & second)
            if "System_ID" not in csv_reader.fieldnames or 'Hostname' not in csv_reader.fieldnames:
                print("the CSV file must contain 'System_ID' and 'Hostname' columns")
                print("Please recheck the contents of the .csv file.")
                input("Press Enter key to exit:")
                sys.exit()

            print(f"Contents of {csvFilePath}: ")
            print("=" * 20)
            for row in csv_reader:
                print(f"System_ID: {row['System_ID']}, Hostname: {row['Hostname']}")
            print("=" * 20)

            csv.reader(file)
            isCorrect = input("\nAre the contents correct? (Y/N): ").strip().upper()
            if isCorrect == 'Y' or isCorrect == 'y':
                print("Proceed to authenticate.....................")
                # Request for authentication token using the provided client id and client secret.
                token = get_token(clientID, clientSecret)

                if token != "":
                    tenant = get_tenant(token)
                    tenantID = tenant[0]
                    tenantRegion = tenant[1]

                    # Uncomment 3 lines below for troubleshooting of authentication if necessary.
                    #print("Retrieved authentication token: "+token)
                    #print("Retrieved tenant id: "+tenantID)
                    #print("Retrieved tenant region: "+tenantRegion)

                    # Prepare log file for writing
                    with open (logFileName, mode='a', newline='') as log:
                        writer = csv.DictWriter(log, fieldnames=logFileheaders)
                        writer.writeheader()

                        # For each System_ID, check if there's existing group membership. If none, skip and write a log.
                        # If there is a group membership, remove
                        with open(csvFilePath, mode='r') as file2:
                            csv_reader2 = csv.DictReader(file2)
                            
                            print("\nContents of the CSV file:")
                            print("-" * 10)
                            for row2 in csv_reader2:
                                print(f"Collecting information for: {row2['System_ID']} ({row2['Hostname']})")
                                systemid = row2['System_ID']
                                systemhostname = row2['Hostname']

                                requestUrl = tenantRegion+"/endpoint/v1/endpoints/"+systemid+""
                                requestpayload={}
                                requestfiles={}
                                requestHeaders = {
                                    'X-Tenant-ID': tenantID,
                                    "Authorization": "Bearer "+ token,
                                    "Accept": "application/json"
                                }
                                # Uncomment this line below for troubleshooting url request of endpoint details.
                                #print(requestUrl)
                                endpoint_details = requests.get(requestUrl, headers=requestHeaders, data=requestpayload, files=requestfiles)
                                item2 = json.loads(endpoint_details.text)



                                if('group' in item2):
                                    groupName = item2['group']['name']
                                    # Uncomment this line below for troubleshooting endpoint group membership.
                                    #print("Member of group: "+groupName)
                                    #print("Getting Group ID...")
                                    allGroups = get_all_groups(token, tenantRegion, tenantID)
                                    groupID = find_group_id_by_name(allGroups, groupName)
                                    print(f"Removing from group: {groupName} ({groupID}).")

                                    try:
                                        removalResult = remove_agent_from_group(token, tenantRegion, tenantID, systemid, groupID)
                                        #print(f"Delete URL request: {removalResult[1]}")
                                        statusMessage = removalResult[0]
                                        #print("Successfully removed endpoint from group. Writing log...")
                                        logFileRow = [
                                            {'System_ID': f'{systemid}', 'Hostname': f'{systemhostname}', 'Group_ID': f'{groupID}', 'GroupName': f'{groupName}', 'RemovalStatus': f'{statusMessage}'}
                                        ]
                                        for row in logFileRow:
                                            writer.writerows(logFileRow)
                                    except requests.exceptions.HTTPError as http_err:
                                        print("Failed to remove endpoint from group. Writing log...")
                                        print(f"An error occured during http request: {http_err}")
                                        logFileRow = [
                                            {'System_ID': f'{systemid}', 'Hostname': f'{systemhostname}', 'Group_ID': f'{groupID}', 'GroupName': f'{groupName}', 'RemovalStatus': f'Failed: {http_err}'}
                                        ]
                                        for row in logFileRow:
                                            writer.writerows(logFileRow)
                                    except Exception as err:
                                        print("Failed to remove endpoint from group.")
                                        print(f"An unknown error occurred: {err}")
                                        logFileRow = [
                                            {'System_ID': f'{systemid}', 'Hostname': f'{systemhostname}', 'Group_ID': f'{groupID}', 'GroupName': f'{groupName}', 'RemovalStatus': f'Failed: {err}'},
                                        ]
                                        for row in logFileRow:
                                            writer.writerows(logFileRow)
                                    print("")
                                else:
                                    groupName = "None"
                                    print("Member of group: "+groupName+". ")
                                    # Uncomment this line below for troubleshooting endpoint group membership.
                                    #print("Skip removal from group.\n")
                                    logFileRow = [
                                        {'System_ID': f'{systemid}', 'Hostname': f'{systemhostname}', 'Group_ID': 'None', 'GroupName': f'{groupName}', 'RemovalStatus': 'Skipped removal from group'}
                                    ]
                                    for row in logFileRow:
                                        writer.writerows(logFileRow)
                                    print("")
                            print("-" * 10)
  
                            # Uncomment below 2 lines for troubleshooting group query.
                            #print(allGroups)
                            #print(f"\n\nTotal groups found: {len(allGroups)}")
                        
                else:
                    print("Unable to authenticate, retrieve token and retrieve tenant information.")
                    input("Press Enter key to exit:")
                    sys.exit()
            else:
                print("Please re-enter the full path of correct .csv file")
                print("Press Enter key to exit:")
                sys.exit()
    #except Exception as e:
    #    print(f"An error occured while attempting to open the file: {csvFilePath}. {e}")
    #    print("Please ensure read permission on the file.")
    #    input("Press Enter key to exit:")
    #    sys.exit()
else:
    print("Unable to access the specified .csv file. Please try again.")
    input("Press Enter key to exit:")
    sys.exit()
