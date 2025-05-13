"""
UNICOM TIC Banking System
-------------------------------
Made by: Abdul Baasith

This is a simple command-line banking app built with Python.

- creating accounts
- checking balance
- depositing and withdrawing money
- transferring money between accounts
- getting monthly interest (only for savings)

Data is saved in text files

Text Files Used
- AccountDetails.txt     - stores account number, name, and balance
- CustomerProfiles.txt   - stores full customer info like NIC, DOB, phone, etc.
- transactions.txt       - logs all money-related actions
- credentials.txt        - keeps usernames, hashed passwords, and roles (admin/user)
- change_log.txt         - records any profile updates
- deactivation_log.txt   - logs when accounts are turned off
- interestlog.txt        - keeps a history of interest added each month

Python Modules Used:
- pwinput   - for hiding passwords during typing
- bcrypt    - to hash passwords (for security)
- datetime  - to handle dates (DOB, interest, transactions)
- os        - to clear the terminal screen
- tabulate  - to print data in nice tables
- colorama  - to add color to messages (errors, success, etc.)
"""


import pwinput
import bcrypt
from tabulate import tabulate
import datetime
import os
from colorama import Fore, init
init(autoreset=True)

'''
This function takes a plain password and turns it into a hashed one using bcrypt.
It adds some extra random stuff (called salt) to make it more secure.
So even if someone opens the file, they can't read the real password.
'''

def hash_password(password):

    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


'''
This checks if the password the user typed matches the saved (hashed) one.
It uses bcrypt so we don’t have to store real passwords.
'''

def check_password(password, hashed):

    return bcrypt.checkpw(password.encode(), hashed.encode())



def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')



def accountInactive(accNo):
    try:
        with open('CustomerProfiles.txt', 'r') as f:
            for line in f:
                if line.startswith(accNo + "|"):
                    parts = line.strip().split('|')
                    return parts[-1] == "Inactive"
    except FileNotFoundError:
        return False
    return False



def generateAccountNumber():
    highest = 2003  

    try:
        with open("AccountDetails.txt", 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 1:
                    accNo = parts[0]
                    if accNo.isdigit():
                        accNo_int = int(accNo)
                        if accNo_int > highest:
                            highest = accNo_int
    except FileNotFoundError:
        pass  
    except Exception as e:
        print(Fore.RED + " Error reading account file: " + str(e))

    next_acc_no = highest + 1
    return str(next_acc_no)

def login():
    print(Fore.GREEN + "\t___________________________________________________________________________________")
    print(Fore.GREEN + "\t|                                                                                  |")
    print(Fore.GREEN + "\t|          ================= Welcome To Unicom Tic Bank ==================         |")
    print(Fore.GREEN + "\t|                                                                                  |")
    print(Fore.GREEN + "\t___________________________________________________________________________________")
    print("")
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t|                 ==================== LOGIN ====================                  |")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print("")

    username = input("\t\t\t\tUsername: ").strip()
    password = pwinput.pwinput("\t\t\t\tPassword: ").strip()

    try:
        with open("credentials.txt", 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) == 3:
                    file_username, file_password, role = parts
                    if file_username == username and check_password(password, file_password):
                        if role == 'user':
                            accNo = username.replace('user', '')
                            try:
                                with open('CustomerProfiles.txt', 'r') as profile:
                                    for line in profile:
                                        if line.startswith(accNo + "|"):
                                            parts = line.strip().split('|')
                                            if len(parts) == 9:
                                                parts.append("Active")  
                                            if parts[-1] == "Inactive":
                                                print(Fore.RED + " Your account is inactive. Contact the bank.")
                                                return None
                                            break
                            except FileNotFoundError:
                                print(Fore.RED + f"\n Customer file 'CustomerProfiles.txt' not found.")
                                return None
                            except Exception as e:
                                print(Fore.RED + f"\n Error accessing customer file: {e}")
                                return None

                            print(Fore.GREEN + f"\nLogin successful! Logged in as User.")
                            return role, accNo

                        print(Fore.GREEN + f"\nLogin successful! Logged in as Admin.")
                        return role, None

    except FileNotFoundError:
        print(Fore.RED + " Credentials file not found.")
        return None
    except Exception as e:
        print(Fore.RED + f" Error reading credentials file: {e}")
        return None

    print(Fore.RED + "\nLogin failed. Invalid username or password.")
    return None


def changePassword(username):
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t|             ================= Change Password ==================                 |")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print("")
    try:
        with open("credentials.txt", "r") as f:
            lines = f.readlines()

        updated_lines = []
        found = False

        for line in lines:
            parts = line.strip().split(':')
            if len(parts) == 3 and parts[0] == username:
                found = True
                current_hashed = parts[1]
                current_pw = pwinput.pwinput("Enter current password: ")

                if not check_password(current_pw, current_hashed):
                    print(Fore.RED + " Incorrect current password.")
                    return

                new_pw = pwinput.pwinput("Enter new password: ")
                confirm_pw = pwinput.pwinput("Confirm new password: ")

                if new_pw != confirm_pw:
                    print(Fore.RED + " Passwords do not match.")
                    return

                hashed_pw = hash_password(new_pw)
                updated_lines.append(f"{username}:{hashed_pw}:{parts[2]}\n")
                print(Fore.GREEN + " Password changed successfully.")
            else:
                updated_lines.append(line)

        with open("credentials.txt", "w") as f:
            f.writelines(updated_lines)

        if not found:
            print(Fore.RED + " Username not found.")

    except Exception as e:
        print(Fore.RED + f" Failed to change password: {e}")




def getValidatedInput(prompt, fieldName, validationType=None):
    while True:
        value = input(prompt).strip()

        if value == "":
            print(Fore.RED + f"Oops! {fieldName} can't be empty. Try again.")
            continue

        if validationType == "nic":
            if len(value) == 10:
                if not value[:9].isdigit() or value[-1].upper() not in ['V', 'X']:
                    print(Fore.RED + "Invalid NIC! Should be 9 digits and end with V or X.")
                    continue
            elif len(value) == 12:
                if not value.isdigit():
                    print(Fore.RED + "NIC with 12 characters must have only numbers.")
                    continue
            else:
                print(Fore.RED + "NIC must be either 10 or 12 characters long.")
                continue

        elif validationType == "dob":
            try:
                datetime.datetime.strptime(value, "%Y-%m-%d")
            except:
                print(Fore.RED + "Date format should be YYYY-MM-DD (e.g., 2000-01-01).")
                continue

        elif validationType == "phone":
            if not value.isdigit() or len(value) != 10:
                print(Fore.RED + "Phone number must have exactly 10 digits.")
                continue

        elif validationType == "email":
            if "@" not in value or "." not in value:
                print(Fore.RED + "Invalid email. Must contain '@' and a domain.")
                continue
            if value.startswith("@") or value.endswith("@") or ".." in value:
                print(Fore.RED + "Email looks wrong. Check the format again.")
                continue

        elif validationType == "gender":
            if value.lower() not in ["male", "female"]:
                print(Fore.RED + "Please enter Male or Female only.")
                continue
            return value.capitalize()

        
        return value


def searchCustomerBy(field, value):
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t|          ================= Search Customer Accounts ==================           |")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print("")
    try:
        found = False
        with open('CustomerProfiles.txt', 'r') as f:
            for line in f:
                parts = line.strip().split('|')

                if field == "nic":
                    if parts[2] == value:
                        print(Fore.CYAN + "\n---- Customer Found ----")
                        print("Account No  :", parts[0])
                        print("Name        :", parts[1])
                        print("NIC         :", parts[2])
                        print("Phone       :", parts[4])
                        print("Email       :", parts[5])
                        print("Account Type:", parts[8])
                        print("Status      :", parts[9])
                        found = True

                if field == "phone":
                    if parts[4] == value:
                        print(Fore.CYAN + "\n---- Customer Found ----")
                        print("Account No  :", parts[0])
                        print("Name        :", parts[1])
                        print("NIC         :", parts[2])
                        print("Phone       :", parts[4])
                        print("Email       :", parts[5])
                        print("Account Type:", parts[8])
                        print("Status      :", parts[9])
                        found = True

        if found == False:
            print(Fore.RED + " No matching customer found.")
    except FileNotFoundError:
        print(Fore.RED + " Customer data file not found.")
    except IndexError:
        print(Fore.RED + " Data format issue in customer file.")
    except Exception as e:
        print(Fore.RED + f" Unexpected error occurred: {e}")


def createAccount():
    clearScreen()
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t|          ================= Create New Bank Account ==================            |")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print("")

    try:
        name = getValidatedInput("\t\t\t\tFull Name: ", "Name").upper()
        nic = getValidatedInput("\t\t\t\tNIC/Passport No: ", "NIC/Passport Number", "nic")
        dob = getValidatedInput("\t\t\t\tDate of Birth (YYYY-MM-DD): ", "Date of Birth", "dob")
        gender = getValidatedInput("\t\t\t\tGender (Male/Female): ", "Gender", "gender")
        phone = getValidatedInput("\t\t\t\tPhone Number: ", "Phone Number", "phone")
        email = getValidatedInput("\t\t\t\tEmail Address: ", "Email", "email")
        address = getValidatedInput("\t\t\t\tResidential Address: ", "Residential Address")
        while True:
            print(Fore.CYAN + "\n\t\t\t\tChoose Account Type:")
            print("\t\t\t\t1. Savings (Interest Eligible)")
            print("\t\t\t\t2. Current (No Interest)")
            account_choice = input("\t\t\t\tEnter 1 or 2: ").strip()

            if account_choice == '1':
                accountType = "Savings"
                break
            elif account_choice == '2':
                accountType = "Current"
                break
            else:
                print(Fore.RED + "\t\t\t\t Invalid choice. Please enter 1 or 2.")

        while True:
            try:
                balance = float(input("Initial Deposit Amount (>=0): "))
                if balance < 0:
                    print(Fore.RED + "Deposit amount must be 0 or more.")
                else:
                    break
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a numeric amount.")

        
        

        accNo = generateAccountNumber()
        username = "user" + accNo
        password = "pass" + accNo
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            
            with open("credentials.txt", 'a') as f:
                f.write(f"{username}:{hash_password(password)}:user\n")

            
            with open("AccountDetails.txt", 'a') as f:
                f.write(f"{accNo}|{name}|{balance}\n")

           
            with open("CustomerProfiles.txt", 'a') as f:
                f.write(f"{accNo}|{name}|{nic}|{dob}|{phone}|{email}|{address}|{gender}|{accountType}|Active\n")

            
            with open("transactions.txt", 'a') as f:
                f.write(f"{accNo}|Opening Balance|{balance}|{timestamp}\n")

        except Exception as e:
            print(Fore.RED + f" Failed to save account: {e}")
            return

        print(Fore.GREEN + "\n Account Created Successfully!")
        print(Fore.GREEN + "Account Number :", accNo)
        print(Fore.GREEN + "Username       :", username)
        print(Fore.GREEN + "Password       :", password)
        print(Fore.GREEN + "Date of Birth  :", dob)
        print(Fore.GREEN + "Gender         :", gender)
        print(Fore.GREEN + "Account Type   :", accountType)

    except Exception as e:
 
        print(Fore.RED + f" Unexpected error occurred: {e}")


'''
This reads the CustomerProfiles.txt file and shows the matching customer info
in a nice table format using tabulate.
'''

def readCustomer(role, acc_no=None):
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t|       ================= View Customer Profile ==================                 |")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print("")
    accNo = input(Fore.CYAN + "Enter Account Number to View: ").strip()

    if role != 'admin' and accNo != acc_no:
        print(Fore.RED + " You can only view your own profile.")
        return

    if accountInactive(accNo) == True:
        print(Fore.RED + " Cannot access an inactive account.")
        return

    found = False

    try:
        with open('CustomerProfiles.txt', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + " Customer profile file not found.")
        return
    except Exception as e:
        print(Fore.RED + f" Error reading customer file: {e}")
        return

    try:
        with open('CustomerProfiles.txt', 'w') as f:
            for line in lines:
                line = line.strip()
                parts = line.split('|')

                if len(parts) >= 10:
                    acc_from_file = parts[0]

                    if acc_from_file == accNo:
                        status = parts[9]
                        if status == "Inactive":
                            print(Fore.RED + " This customer is inactive.")
                            f.write(line + "\n")
                            return

                        print(Fore.CYAN + "\n---- Customer Profile ----")
                        print(tabulate([
                            ["Account No", parts[0]],
                            ["Name", parts[1]],
                            ["NIC", parts[2]],
                            ["Date of Birth", parts[3]],
                            ["Phone", parts[4]],
                            ["Email", parts[5]],
                            ["Address", parts[6]],
                            ["Gender", parts[7]],
                            ["Account Type", parts[8]],
                            ["Status", parts[9]]
                        ], headers=["Name", "Value"], tablefmt="fancy_grid"))

                        found = True

                f.write(line + "\n")

        if found == False:
            print(Fore.RED + " Customer not found.")

    except Exception as e:
        print(Fore.RED + f" Failed to display customer profile: {e}")


'''
This changes an account from Inactive back to Active
and writes it down in the log file.
'''

def restoreCustomer():
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t|             ================= Restore Customer ==================                |")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print("")
    accNo = input(Fore.CYAN + "Enter Account Number to Restore: ").strip()
    restored = False

    try:
        with open('CustomerProfiles.txt', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + " Customer profile file not found.")
        return
    except Exception as e:
        print(Fore.RED + f" Error reading file: {e}")
        return

    try:
        with open('CustomerProfiles.txt', 'w') as f:
            for line in lines:
                line = line.strip()
                parts = line.split('|')

                if len(parts) >= 10:
                    acc_from_file = parts[0]

                    if acc_from_file == accNo:
                        status = parts[9]
                        if status == "Active":
                            print(Fore.GREEN + " Customer already active.")
                            f.write(line + "\n")
                        else:
                            parts[9] = "Active"

                            updatedLine = parts[0]
                            index = 1
                            while index < len(parts):
                                updatedLine = updatedLine + "|" + parts[index]
                                index = index + 1

                            f.write(updatedLine + "\n")
                            restored = True
                            print(Fore.GREEN + " Customer restored.")
                    else:
                        f.write(line + "\n")
                else:
                    f.write(line + "\n")

        if restored == False:
            print(Fore.RED + " Account not found or already active.")
    except Exception as e:
        print(Fore.RED + f" Error updating file: {e}")



def updateCustomer():
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t|               ================= Update Customer ==================               |")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print("")
    accNo = input(Fore.CYAN + "Enter Account Number to Update: ").strip()

    if accountInactive(accNo):
        print(Fore.RED + " Cannot update an inactive account.")
        return

    updated = False

    try:
        with open('CustomerProfiles.txt', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + " Customer profile file not found.")
        return
    except Exception as e:
        print(Fore.RED + " Error reading file: " + str(e))
        return

    try:
        with open('CustomerProfiles.txt', 'w') as f, open('change_log.txt', 'a') as log:
            for line in lines:
                line = line.strip()
                parts = line.split('|')

                if len(parts) >= 10 and parts[0] == accNo:
                    print("\n ------ Current Details ------")
                    print("1. Phone    : " + parts[4])
                    print("2. Email    : " + parts[5])
                    print("3. Address  : " + parts[6])
                    print("4. Name     : " + parts[1])
                    print("5. NIC      : " + parts[2])
                    print("6. DOB      : " + parts[3])
                    print("7. Gender   : " + parts[7])
                    print("0. Cancel Update")

                    choice = input("\nWhich field do you want to update? (1–7): ").strip()

                    if choice == "1":
                        old = parts[4]
                        parts[4] = getValidatedInput("New Phone Number: ", "Phone", "phone")
                        log.write(accNo + f" - Phone changed from {old} to {parts[4]}\n")

                    elif choice == "2":
                        old = parts[5]
                        parts[5] = getValidatedInput("New Email: ", "Email", "email")
                        log.write(accNo + f" - Email changed from {old} to {parts[5]}\n")

                    elif choice == "3":
                        old = parts[6]
                        parts[6] = getValidatedInput("New Address: ", "Address")
                        log.write(accNo + f" - Address changed from {old} to {parts[6]}\n")

                    elif choice == "4":
                        old = parts[1]
                        parts[1] = getValidatedInput("New Full Name: ", "Name").upper()
                        log.write(accNo + f" - Name changed from {old} to {parts[1]}\n")

                    elif choice == "5":
                        old = parts[2]
                        parts[2] = getValidatedInput("New NIC: ", "NIC", "nic")
                        log.write(accNo + f" - NIC changed from {old} to {parts[2]}\n")

                    elif choice == "6":
                        old = parts[3]
                        parts[3] = getValidatedInput("New Date of Birth (YYYY-MM-DD): ", "Date of Birth", "dob")
                        log.write(accNo + f" - DOB changed from {old} to {parts[3]}\n")

                    elif choice == "7":
                        old = parts[7]
                        while True:
                            gender = input("Enter Gender (Male/Female): ").strip().capitalize()
                            if gender in ["Male", "Female"]:
                                parts[7] = gender
                                log.write(accNo + f" - Gender changed from {old} to {gender}\n")
                                break
                            else:
                                print(Fore.RED + " Invalid input. Please enter 'Male' or 'Female'.")

                    elif choice == "0":
                        print(Fore.RED + "Update cancelled.")
                        f.write(line + "\n")
                        continue
                    else:
                        print(Fore.RED + "Invalid choice. Skipping update.")
                        f.write(line + "\n")
                        continue

                    updated_line = "|".join(parts)
                    f.write(updated_line + "\n")
                    updated = True

                else:
                    f.write(line + "\n")

        if not updated:
            print(Fore.RED + " Account not found or no updates made.")

    except Exception as e:
        print(Fore.RED + f" Error updating file: {e}")


'''
Instead of deleting the account, this just marks it as Inactive
and saves the reason in deactivation_log.txt.
'''
def softDeleteCustomer(accNo=None):
    confirmed = input("Are you sure you want to mark this customer as inactive? (Y/N): ").strip()
    confirmed = confirmed.lower()

    if confirmed != "y"  :
        print(Fore.RED + " Deletion cancelled.")
        return

    reason = input(Fore.CYAN + "Enter reason for deactivation: ").strip()
    deleted = False

    try:
        with open('CustomerProfiles.txt', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + " Customer file not found.")
        return
    except Exception as e:
        print(Fore.RED + " Error reading customer file: " + str(e))
        return

    try:
        with open('CustomerProfiles.txt', 'w') as f, open('deactivation_log.txt', 'a') as log:
            for line in lines:
                line = line.strip()
                parts = line.split('|')

                if len(parts) >= 10:
                    acc_from_file = parts[0]

                    if acc_from_file == accNo:
                        status = parts[9]

                        if status == "Inactive":
                            print(Fore.RED + " Already inactive.")
                            rebuilt_line = parts[0]
                            i = 1
                            while i < len(parts):
                                rebuilt_line = rebuilt_line + "|" + parts[i]
                                i = i + 1
                            f.write(rebuilt_line + "\n")
                        else:
                            parts[9] = "Inactive"

                            rebuilt_line = parts[0]
                            i = 1
                            while i < len(parts):
                                rebuilt_line = rebuilt_line + "|" + parts[i]
                                i = i + 1
                            f.write(rebuilt_line + "\n")

                            log.write(accNo + " | Deactivated on " + str(datetime.datetime.now()) + " | Reason: " + reason + "\n")
                            deleted = True
                            print(Fore.CYAN + " Customer marked as Inactive.")
                    else:
                        f.write(line + "\n")
                else:
                    f.write(line + "\n")

        if deleted == False:
            print(Fore.RED + " Account not found.")

    except Exception as e:
        print(Fore.RED + " Error updating customer file: " + str(e))



'''
Checks if the user can access the account, makes sure it's active,
adds the deposit to the balance, and saves the transaction.
'''
def deposit(role, acc_no=None):
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t|                   ================= Deposit ==================                   |")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print("")

    entered = input(Fore.CYAN + "Enter account number: ").strip()

    if role != "admin" and entered != acc_no:
        print(Fore.RED + " You can only deposit into your own account.")
        return

    if accountInactive(entered):
        print(Fore.RED + " Cannot deposit to an inactive account.")
        return

    
    try:
        with open("AccountDetails.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + " Account file not found.")
        return

    account_found = False
    updated_lines = []

    try:
        amount_input = input(Fore.CYAN + "Amount to deposit: ").strip()
        amount = float(amount_input)
        if amount <= 0:
            print(Fore.RED + " Deposit amount must be greater than 0.")
            return
    except ValueError:
        print(Fore.RED + " Invalid amount. Please enter a valid number.")
        return

    try:
        for line in lines:
            parts = line.strip().split("|")
            if len(parts) == 3 and parts[0] == entered:
                name = parts[1]
                current_balance = float(parts[2])
                new_balance = current_balance + amount
                updated_lines.append(f"{entered}|{name}|{new_balance}\n")
                account_found = True
            else:
                updated_lines.append(line)

        if not account_found:
            print(Fore.RED + " Account not found.")
            return

        
        with open("AccountDetails.txt", "w") as f:
            f.writelines(updated_lines)

        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("transactions.txt", "a") as f:
            f.write(f"{entered}|Deposit|{amount}|{timestamp}\n")

        print(Fore.GREEN + f" Rs.{amount:.2f} deposited successfully into account {entered}.")

    except Exception as e:
        print(Fore.RED + f" Failed to process deposit: {e}")



'''
Makes sure there's enough money, then subtracts the amount
and records the withdrawal in the file.
'''

def withdraw(role, acc_no=None):
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t|                   ================= Withdraw ==================                  |")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print("")

    entered = input(Fore.CYAN + "Enter account number: ").strip()

    if role != "admin" and entered != acc_no:
        print(Fore.RED + " You can only withdraw from your own account.")
        return

    if accountInactive(entered):
        print(Fore.RED + " Cannot withdraw from an inactive account.")
        return

    
    try:
        with open("AccountDetails.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + " Account file not found.")
        return

    account_found = False
    updated_lines = []

    try:
        amount_input = input(Fore.CYAN + "Amount to withdraw: ").strip()
        amount = float(amount_input)
        if amount <= 0:
            print(Fore.RED + " Withdrawal amount must be greater than 0.")
            return
    except ValueError:
        print(Fore.RED + " Invalid amount. Please enter a valid number.")
        return

    for line in lines:
        parts = line.strip().split("|")
        if len(parts) == 3 and parts[0] == entered:
            name = parts[1]
            current_balance = float(parts[2])

            if amount > current_balance:
                print(Fore.RED + " Insufficient funds for this withdrawal.")
                return

            new_balance = current_balance - amount
            updated_lines.append(f"{entered}|{name}|{new_balance}\n")
            account_found = True
        else:
            updated_lines.append(line)

    if not account_found:
        print(Fore.RED + " Account not found.")
        return

    try:
        
        with open("AccountDetails.txt", "w") as f:
            f.writelines(updated_lines)

        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("transactions.txt", "a") as f:
            f.write(f"{entered}|Withdraw|{amount}|{now}\n")

        print(Fore.GREEN + f" Rs.{amount:.2f} withdrawn successfully from account {entered}.")

    except Exception as e:
        print(Fore.RED + f" Withdrawal failed due to an error: {e}")



'''
Shows the balance for the given account,
but only if the user has permission to view it.
'''

def checkBalance(role, acc_no=None):
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t|                ================= Check Balance ==================                |")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print("")

    entered = input(Fore.CYAN + "Enter account number: ").strip()

    if role != "admin" and entered != acc_no:
        print(Fore.RED + " You can only check your own balance.")
        return

    if accountInactive(entered):
        print(Fore.RED + " Cannot check balance for an inactive account.")
        return

    try:
        with open("AccountDetails.txt", "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 3 and parts[0] == entered:
                    balance = float(parts[2])
                    print(Fore.GREEN + f" Your current balance is: Rs. {balance:.2f}")
                    return

        print(Fore.RED + " Account not found.")
    except FileNotFoundError:
        print(Fore.RED + " Account file not found.")
    except Exception as e:
        print(Fore.RED + f" Failed to retrieve balance due to an error: {e}")

'''
Reads all transactions from the file and shows them 
in a clean table using tabulate.
'''

def viewTransactions(role, acc_no=None):
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t|             ================= View Transactions ==================               |")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print("")

    entered = input(Fore.CYAN + "Enter account number: ").strip()

    if role != "admin" and entered != acc_no:
        print(Fore.RED + " You can only view your own transactions.")
        return

    if accountInactive(entered):
        print(Fore.RED + " Cannot view transactions for an inactive account.")
        return

    account_exists = False
    try:
        with open("AccountDetails.txt", "r") as acc_file:
            for line in acc_file:
                if line.strip().split("|")[0] == entered:
                    account_exists = True
                    break
    except FileNotFoundError:
        print(Fore.RED + " Account data file not found.")
        return

    if not account_exists:
        print(Fore.RED + " Account not found.")
        return

    transaction_table = []
    index = 1

    try:
        with open("transactions.txt", 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 4 and parts[0] == entered:
                    _, txnType, amount, date = parts
                    transaction_table.append([index, txnType, f"Rs.{amount}", date])
                    index += 1

        print(Fore.CYAN + f"\n Transaction History for Account {entered}:\n")

        if not transaction_table:
            print(Fore.YELLOW + " No transactions recorded for this account.")
        else:
            print(tabulate(transaction_table, headers=["No", "Type", "Amount", "Date"], tablefmt="fancy_grid"))

    except FileNotFoundError:
        print(Fore.YELLOW + " No transactions file found.")
    except Exception as e:
        print(Fore.RED + f" Error retrieving transactions: {e}")



'''
Checks if both accounts exist, then updates their balances
and records the transfer for both sender and receiver.
'''

def transferMoney(role, acc_no=None):
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t|             ================= Transfer Money ==================                  |")
    print(Fore.CYAN + "\t|                                                                                  |")
    print(Fore.CYAN + "\t___________________________________________________________________________________")
    print("")

    fromAcc = input("Sender Account Number: ").strip()
    if role == "user" and fromAcc != acc_no:
        print(" You can only transfer from your own account.")
        return

    toAcc = input("Receiver Account Number: ").strip()
    if fromAcc == toAcc:
        print(" Cannot transfer to the same account.")
        return

    try:
        sender_balance = None
        receiver_balance = None
        account_lines = []

        with open("AccountDetails.txt", "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 3:
                    if parts[0] == fromAcc:
                        sender_balance = float(parts[2])
                    elif parts[0] == toAcc:
                        receiver_balance = float(parts[2])
                    account_lines.append(parts)

        if sender_balance is None:
            print(" Sender account not found.")
            return
        if receiver_balance is None:
            print(" Receiver account not found.")
            return

        try:
            amount = float(input("Amount to transfer: ").strip())
            if amount <= 0:
                print("Transfer amount must be greater than 0.")
                return
            if amount > sender_balance:
                print(" Insufficient balance.")
                return
        except ValueError:
            print(" Invalid amount.")
            return

        updated_lines = []
        for parts in account_lines:
            if parts[0] == fromAcc:
                new_sender_balance = sender_balance - amount
                parts[2] = f"{new_sender_balance:.2f}"
            elif parts[0] == toAcc:
                new_receiver_balance = receiver_balance + amount
                parts[2] = f"{new_receiver_balance:.2f}"

            
            new_line = parts[0]
            i = 1
            while i < len(parts):
                new_line = new_line + "|" + parts[i]
                i += 1
            updated_lines.append(new_line)

        with open("AccountDetails.txt", "w") as f:
            for line in updated_lines:
                f.write(line + '\n')

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("transactions.txt", "a") as txn_file:
            txn_file.write(f"{fromAcc}|Transfer to {toAcc}|{amount:.2f}|{now}\n")
            txn_file.write(f"{toAcc}|Transfer from {fromAcc}|{amount:.2f}|{now}\n")

        print(f" Rs.{amount:.2f} successfully transferred from {fromAcc} to {toAcc}.")

    except FileNotFoundError:
        print(" AccountDetails.txt file not found.")
    except Exception as e:
        print(f" An unexpected error occurred: {e}")



'''
Adds monthly interest to savings accounts if it hasn’t been added yet,
and updates the balances accordingly.
'''

def applyMonthlyInterest():
    interestRateAnnual = 0.03
    interestRateMonthly = interestRateAnnual / 12
    today = datetime.date.today()
    alreadyApplied = []

    try:
        with open("interestlog.txt", "r") as log:
            for line in log:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    acc = parts[0]
                    date = parts[1]
                    try:
                        logDate = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                        if logDate.month == today.month and logDate.year == today.year:
                            alreadyApplied.append(acc)
                    except:
                        continue
    except FileNotFoundError:
        pass

    accountLines = []
    try:
        with open("AccountDetails.txt", "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 3:
                    accNo = parts[0]
                    name = parts[1]
                    bal = float(parts[2])
                    accountLines.append([accNo, name, bal])
    except FileNotFoundError:
        print(Fore.RED + " AccountDetails.txt not found.")
        return

    try:
        with open("CustomerProfiles.txt", "r") as f:
            profiles = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + " CustomerProfiles.txt not found.")
        return

    try:
        newProfiles = []
        with open("interestlog.txt", "a") as log, open("transactions.txt", "a") as txn:
            for line in profiles:
                parts = line.strip().split('|')
                if len(parts) >= 10:
                    acc = parts[0]
                    accType = parts[8]
                    status = parts[9]

                    if accType == "Savings" and status == "Active" and acc not in alreadyApplied:
                        for accLine in accountLines:
                            if accLine[0] == acc:
                                oldBalance = accLine[2]
                                interest = (oldBalance * interestRateMonthly)
                                newBalance = (oldBalance + interest)

                                accLine[2] = float(format(newBalance, ".2f"))
                                formattedInterest = format(interest, ".2f")
                                formattedRate = format(interestRateMonthly * 100, ".2f")

                                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                log.write(f"{acc}|{today}|{formattedInterest}|{formattedRate}%\n")
                                txn.write(f"{acc}|Interest|{formattedInterest}|{now}\n")
                                break
                newProfiles.append(line.strip())

        with open("CustomerProfiles.txt", "w") as f:
            for p in newProfiles:
                f.write(p + "\n")

        with open("AccountDetails.txt", "w") as f:
            for accLine in accountLines:
                f.write(f"{accLine[0]}|{accLine[1]}|{format(accLine[2], '.2f')}\n")

        print(Fore.GREEN + " Interest applied successfully.")

    except Exception as e:
        print(Fore.RED + f" Error applying interest: {e}")


'''
Reads the interestlog.txt file and shows account number, date,
interest amount, and rate in a nice table.
'''

def viewInterestHistory():
    applyMonthlyInterest()
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t|              ================= Intrest History ==================                |")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print("")
    interestRecords = []

    try:
        with open('interestlog.txt', 'r') as log:
            for line in log:
                line = line.strip()
                parts = line.split('|')

                if len(parts) == 4:
                    accNo = parts[0]
                    date = parts[1]
                    amount = parts[2]
                    rate = parts[3]

                    formattedAmount = "Rs." + amount
                    row = [accNo, date, formattedAmount, rate]
                    interestRecords.append(row)

    except FileNotFoundError:
        print(Fore.YELLOW + " No interest records found.")
        return
    except Exception as e:
        print(Fore.RED + " Error reading interest log: " + str(e))
        return

    if len(interestRecords) > 0:
       
        print(tabulate(interestRecords, headers=["Account No", "Date", "Interest Amount", "Rate"], tablefmt="fancy_grid"))
    else:
        print(Fore.YELLOW + " No interest entries to display.")




'''
Shows the admin menu with options to create, update, and manage
accounts, transactions, and logs.
'''

def adminMenu(role):
    while True:
        input(Fore.YELLOW + "\nPress Enter to Enter to menu...")
        clearScreen()
        print(Fore.CYAN+"\t___________________________________________________________________________________")
        print(Fore.CYAN+"\t|                                                                                  |")
        print(Fore.CYAN+"\t|                 ================= Admin Menu ==================                  |")
        print(Fore.CYAN+"\t|                                                                                  |")
        print(Fore.CYAN+"\t___________________________________________________________________________________")
        print("")
        menu = [
            ["1", "Create Account"],
            ["2", "View Customer Profile"],
            ["3", "Update Customer Details"],
            ["4", "Delete Customer"],
            ["5", "Deposit"],
            ["6", "Withdraw"],
            ["7", "Check Balance"],
            ["8", "Transaction History"],
            ["9", "Transfer Money"],
            ["10", "Restore Inactive Customer"],
            ["11", "View Interest History"],
            ["12", "Search Customer by NIC/Phone"],
            ["0", "Logout"]
        ]
        table = tabulate(menu, headers=["Option", "Description"], tablefmt="fancy_grid")

        for i in table.split('\n'):
            print("\t\t\t\t"+ i)
        

        try:
            choice = input(Fore.YELLOW + "\t\t\t\tSelect an Option (0–11): ").strip()
        except Exception as e:
            print(Fore.RED + f" Input error: {e}")
            input(Fore.YELLOW + "\nPress Enter to continue...")
            continue

        if choice == '1':
            createAccount()
        elif choice == '2':
            readCustomer(role)
        elif choice == '3':
            updateCustomer()
        elif choice == '4':
            print(Fore.CYAN+"\t___________________________________________________________________________________")
            print(Fore.CYAN+"\t|                                                                                  |")
            print(Fore.CYAN+"\t|          ================= Delete Customer Accounts ==================           |")
            print(Fore.CYAN+"\t|                                                                                  |")
            print(Fore.CYAN+"\t___________________________________________________________________________________")
            print("")
            accNo = input(Fore.CYAN + "Enter Account Number to Deactivate: ").strip()
            softDeleteCustomer(accNo)
        elif choice == '5':
            deposit(role)
        elif choice == '6':
            withdraw(role)
        elif choice == '7':
            checkBalance( role)
        elif choice == '8':
            viewTransactions( role)
        elif choice == '9':
            transferMoney(role)
        elif choice == '10':
            restoreCustomer()
        elif choice == '11':
            viewInterestHistory()
        elif choice == '12':
            print(Fore.CYAN + "\n Search Customer")
            print("1. By NIC")
            print("2. By Phone")
            search_choice = input("Select an option (1/2): ").strip()
            
            if search_choice == "1":
                nic = input("Enter NIC: ").strip()
                searchCustomerBy("nic", nic)
            elif search_choice == "2":
                phone = input("Enter Phone Number: ").strip()
                searchCustomerBy("phone", phone)
            else:
                print(Fore.RED + "Invalid selection.")


        elif choice == '0':
            print(Fore.CYAN + " Logging out of Admin Menu.")
            break
        else:
            print(Fore.RED + " Invalid choice. Please select from 0 to 11.")

        input(Fore.YELLOW + "\nPress Enter to return to menu...")




def userMenu(role, acc_no):
    while True:
        clearScreen()
        print(Fore.CYAN+"\t___________________________________________________________________________________")
        print(Fore.CYAN+"\t|                                                                                  |")
        print(Fore.CYAN+"\t|                 ================= User  Menu ==================                  |")
        print(Fore.CYAN+"\t|                                                                                  |")
        print(Fore.CYAN+"\t___________________________________________________________________________________")
        print("")
        menu = [
            ["1", "User Profile"],
            ["2", "Deposit"],
            ["3", "Withdraw"],
            ["4", "Check Balance"],
            ["5", "Transaction History"],
            ["6", "Transfer Money"],
            ["7", "Change Password"],
            ["0", "Logout"]
        ]
        table = tabulate(menu, headers=["Option", "Description"], tablefmt="fancy_grid")

        for i in table.split("\n"):
            print("\t\t\t\t"+i)

        try:
            choice = input(Fore.YELLOW + "\t\t\t\tSelect an option (0–6): ").strip()
        except Exception as e:
            print(Fore.RED + f" Input error: {e}")
            input(Fore.YELLOW + "\nPress Enter to continue...")
            continue

        if choice == '1':
            readCustomer(role, acc_no)
        elif choice == '2':
            deposit( role, acc_no)
        elif choice == '3':
            withdraw( role, acc_no)
        elif choice == '4':
            checkBalance( role, acc_no)
        elif choice == '5':
            viewTransactions( role, acc_no)
        elif choice == '6':
            transferMoney(role, acc_no)
        elif choice == '7':
            username = "user" + acc_no
            changePassword(username)

        elif choice == '0':
            print(Fore.CYAN + " Logging out of User Menu.")
            break
        else:
            print(Fore.RED + " Invalid choice. Please select from 0 to 6.")

        input(Fore.YELLOW + "\nPress Enter to return to menu...")




def startMenu():
    while True:
        try:
            input(Fore.YELLOW + "\nPress Enter to continue...")
            clearScreen()

            
            result = login()

            if result:
                role, acc_no = result
                if role == 'admin':
                    adminMenu( role)
                elif role == 'user':
                    userMenu( role, acc_no)
            else:
                print(Fore.RED + "Access denied.")

            print(Fore.RED + "\n You have been logged out.")
            choice = input(Fore.CYAN + "Press ENTER to login again or type 0 to exit: ").strip()

            if choice == '0':
                print(Fore.CYAN+"\t___________________________________________________________________________________")
                print(Fore.CYAN+"\t|                                                                                  |")
                print(Fore.CYAN+"\t|  ============ Thank you for using Unicom Banking App. Goodbye!  ============     |")
                print(Fore.CYAN+"\t|                                                                                  |")
                print(Fore.CYAN+"\t___________________________________________________________________________________")
                print("")
                break

        except KeyboardInterrupt:
            print(Fore.RED + "\n Interrupted. Exiting application.")
            break
        except Exception as e:
            print(Fore.RED + f" An error occurred: {e}")
            input(Fore.YELLOW + "Press Enter to try again...")


startMenu()















