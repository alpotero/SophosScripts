import csv
import os
import requests, json


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


def get_endpoint_details(token, tenant_id, tenant_region, endpoint_id):
    url = tenant_region + f'{"/endpoint/v1/endpoints/"+endpoint_id+"?view=full"}'
    payload={}
    files={}
    headers = {
        'X-Tenant-ID': tenant_id,
        'Authorization': 'Bearer '+token
    }

    response = requests.request("GET", url, headers=headers, data=payload, files=files)
    item = json.loads(response.text)

    return [item];
#===================================================================================

# Input API details
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

endpoint_id = "6c0eaf72-1950-4f01-8cfe-3017c78b3747"
endpoint_details = get_endpoint_details(source_token, source_tenant_id, source_tenant_region, endpoint_id)
print(endpoint_details[0])

endpoint_details_jsond = json.dumps(endpoint_details)
endpoint_details_jsonl = json.loads(endpoint_details_jsond)
print("\n\n\n\n\nGETTING SPECIFIC JSON DETAILS\n")
print(endpoint_details_jsonl[0]['group']['name'])
print(endpoint_details_jsonl[0]['group']['id'])

if ('group' in endpoint_details_jsonl[0]):
    print("Group ID is: "+endpoint_details_jsonl[0]['group']['id'])
else:
    print("errrr")



'''
def pull_name():
  firstname = "Aldrin"
  lastname = "Tadeo"
  return [firstname, lastname];

full_name = pull_name()
print (full_name[0]+" "+full_name[1])
'''