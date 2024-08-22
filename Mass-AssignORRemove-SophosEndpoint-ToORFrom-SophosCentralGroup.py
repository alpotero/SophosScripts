import csv
import os
import requests, json


        file_path = input("Enter the full path of the .csv file: ")

        # Check first if the file exists
        if not os.path.exists(file_path):
            print("The specified file doesn't exist. Please try again.")



def read_and_validate_csv(file_path):
    
    # Present the contents of provided .csv file
    print("\nHere's the contents of: "+file_path)

    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)

            # Check if the required columns exists: first and second
            if "System_ID" not in csv_reader.fieldnames or 'Hostname' not in csv_reader.fieldnames:
                print ("the CSV file must contain 'System_ID' and 'Hostname' columns")
                print (csv_reader.fieldnames)
                return False;
            
            # Else, print the contents of the first two columns
            print("\nContents of the CSV file:")
            print("-" * 40)
            for row in csv_reader:
                print(f"System_ID: {row['System_ID']}, Hostname: {row['Hostname']}")
            print("-" * 40)

            # Ask if the contents are correct
            is_correct = input("\nAre the contents correct? (Y/N): ").strip().upper()
            if is_correct == 'Y':
                #return True
                return main_menu(file_path);
            elif is_correct == 'N':
                return False;
            else:
                print("Invalid input. Please enter 'Y' or 'N'.")
                return False;
            
    except:
        print(f"An error occured while attempting to open the file: "+file_path+".\n\n")
        return False


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




def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Load and check the .csv reference file.")
        print("2. Connect and authenticate to your Sophos Central tenant.")
        print("3. Assign the defined Sophos Central Agents to a group.")
        print("4. Remove the Sophos Central MDR Agents from its current group.")
        print("0. Exit the program.")

        user_choice = input("\nChoose an option. Input number only: ").strip()
        os.system('cls')

        if user_choice=="1":
            # Ask the user for the file location of .csv
            csv_file_path = get_csv_file()

            # Validate the contents of the provided .csv file
            if read_and_validate_csv(csv_file_path):
                break # Go back to the main menu if the contents are correct...
            
        elif user_choice=="2":
            # Ask for Sophos Central API Client ID and Client Secrete
            os.system('cls')
            print("Please enter your source Central API credentials: \n")
            client_id = input("\nEnter Client ID: ")
            client_secret = input("\nEnter Client secret: ")

            # Request for authentication token using the provided client id and client secret.
            source_token = get_token(client_id, client_secret)

            if source_token != "":
                source_tenant = get_tenant(source_token)
                source_tenand_id = source_tenant[0]
                source_tenant_region = source_tenant[1]

            try:
                print("Loaded .csv file: "+csv_file_path)
            except:
                input("No .csv file loaded yet. Press return key to continue...")

            try:
                print("Source tenant info: "+source_tenant)
                print("Source tenant region info: "+source_tenant_region)
                print("Source tenant token info: "+source_token)
            except:
                input("No tenant information or token yet. Press return key to continue...")

            

        elif user_choice=="0":
            os.system('cls')
            print("\nExiting the program... good bye!\n")
            break
        else:
            input("\nSorry I didn't understand your input.\nPress return key to go back to the menu...\n")
            os.system('cls')


if __name__ == "__main__":
    main_menu()