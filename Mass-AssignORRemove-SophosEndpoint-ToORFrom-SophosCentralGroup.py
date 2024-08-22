

def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Load and check the .csv reference file.")
        print("2. Connect and authenticate to your Sophos Central tenant.")
        print("3. Assign the defined Sophos Central Agents to a group.")
        print("4. Remove the Sophos Central MDR Agents from its current group.")
        print("0. Exit the program.")

        user_choice = input("Choose an option. Input number only: ").strip()

        if user_choice=="1":
            asd
        elif user_choice=="0":
            print("Exiting the program")