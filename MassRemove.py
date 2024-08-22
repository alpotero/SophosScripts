import csv
import os
import requests, json
import sys


def get_token(client_id, client_secret):
    token = ""
    url = "https://id.sophos.com/api/v2/oauth2/token"
    payload='grant_type=client_credentials&client_id='+client_id+'&client_secret='+client_secret+'&scope=token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer null'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    token_response = json.loads(response.text)
  
    if ('errorCode' in token_response):
        if (token_response['errorCode'] != "success"):
            os.system('cls')
            print("\nError Message: " + f'{token_response}' + "\n")
            input("\nIncorrect Credentials! Press Enter to try again...")
            os.system('cls')
        elif(token_response['errorCode'] == "success"): 
            token = token_response["access_token"]
    
    else:
     input("Issue with request, please please enter to try again!")
     os.system('cls')
      
    return token;


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














file_path = input("Enter the full path of the .csv file: ")

# Check first if the file exists
if os.path.exists(file_path):
    print("Loaded file is: "+file_path)
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)

            # Check if the required columns exists: first and second
            if "System_ID" not in csv_reader.fieldnames or 'Hostname' not in csv_reader.fieldnames:
                print ("the CSV file must contain 'System_ID' and 'Hostname' columns")
                input("Please Enter the full path of the correct .csv file in correct content format.")
                input("Press return key to continue...")
                sys.exit()
            
            # Else, print the contents of the first two columns
            print("\nContents of the CSV file:")
            print("-" * 40)
            for row in csv_reader:
                print(f"System_ID: {row['System_ID']}, Hostname: {row['Hostname']}")
            print("-" * 40)

            # Ask if the contents are correct
            is_correct = input("\nAre the contents correct? (Y/N): ").strip().upper()
            if is_correct == 'Y':
                print("Please enter your source Central API credentials: \n")
                client_id = input("\nEnter Client ID: ")
                client_secret = input("\nEnter Client secret: ")

                # Request for authentication token using the provided client id and client secret.
                source_token = get_token(client_id, client_secret)

                if source_token != "":
                    source_tenant = get_tenant(source_token)
                    source_tenant_id = source_tenant[0]
                    source_tenant_region = source_tenant[1]

                    print("Retrieved authentication token: "+source_token+"\n")
                    print("Retrieved tenant id: "+source_tenant_id+"\n")
                    print("Retrieved tenant region: "+source_tenant_region+"\n")

                    # For each System_ID, check if there's existing group membership. If none, skip and write a log.
                    # If there is a group membership, remove and write a log.
                    with open(file_path, mode='r') as file:
                        csv_reader = csv.DictReader(file)
                        
                        print("\nContents of the CSV file:")
                        print("-" * 40)
                        for row in csv_reader:
                            print(f"Collecting information for: {row['System_ID']}")
                            systemid = {row['System_ID']}

                            requestUrl = source_tenant_region+"/endpoint/v1/endpoints/"+systemid+""
                            requestpayload={}
                            requestfiles={}
                            requestHeaders = {
                                'X-Tenant-ID': source_tenant_id,
                                "Authorization": "Bearer "+ source_token,
                                "Accept": "application/json"
                            }
                            
                            print(requestUrl)
                            endpoint_details = requests.get(requestUrl, headers=requestHeaders, data=requestpayload, files=requestfiles)
                            item = json.loads(endpoint_details.text)
                            print(item)

                        print("-" * 40)
                        
                else:
                    print("Unable to authenticate, retrieve token and retrieve tenant information.")
                    input("Press return key to continue...")

            elif is_correct == 'N':
                input("Please Enter the full path of the correct .csv file")
                input("Press return key to continue...")
            else:
                print("Invalid input. Please Enter the full path of the correct .csv file")
                input("Press return key to continue...")
    except:
        print(f"An error occured while attempting to open the file: "+file_path+".\n\n")

else:
    print("The specified file doesn't exist. Please try again.")
    input("Press return key to continue...")

