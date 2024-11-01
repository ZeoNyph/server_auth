"""
File: client.py
Author: Mithun Sivanesan, C3403606
Description: This file contains the client program for testing the server for A3.
"""

import requests, getpass, os, hashlib


if __name__ == "__main__":
    ### START CLIENT
    username = 'root'
    print("Using root; bypassing MFA inputs")
    password = hashlib.sha256(getpass.getpass("What is the password assigned to root? (check what was printed on server terminal):").encode()).hexdigest()
    code = ''

    ## test admin console
    print("Testing admin access control; adding user RobertL [Top Secret]")
    r = requests.post("http://127.0.0.1:2250/admin_console/add_user", data={'username': username, 'password': password, 'code': code, 'token': '', 'newUser': ['RobertL', 'seng2250a@gmail.com', 3]})
    print(r.text)
    if not r.text.startswith("Login successful."):
        print("Please make sure you've typed in the correct password.")
        exit()
        
    
    ## test newly added RobertL, security level = Top Secret
    print("Attempting to log in as RobertL.")
    user_pw = hashlib.sha256(getpass.getpass("What is RobertL's generated password? (is in email): ").encode()).hexdigest()
    r = requests.post("http://127.0.0.1:2250/audit_expenses", data={'username': 'RobertL', 'password': user_pw, 'code': '', 'token': ''})
    print(r.text)
    if 'Incorrect password.' in r.text:
        r = requests.post("http://127.0.0.1:2250/admin_console/remove_user", data={'username': username, 'password': user_pw, 'code': '', 'token': '', 'userToRemove': 'RobertL'})
        print("Exiting program.")
        exit()
    user_mfa_code = getpass.getpass("What is the MFA code for RobertL?: ")
    print("Attempting to read expenses.")
    r = requests.post("http://127.0.0.1:2250/audit_expenses", data={'username': 'RobertL', 'password': user_pw, 'code': user_mfa_code, 'token': ''})
    print(r.text)
    if 'Incorrect MFA code' in r.text:
        r = requests.post("http://127.0.0.1:2250/admin_console/remove_user", data={'username': username, 'password': user_pw, 'code': '', 'token': '', 'userToRemove': 'RobertL'})
        os.remove("data/auth.txt")
        print("Exiting program.")
        exit()
    user_token = getpass.getpass("What is RobertL's token? (check email inbox) (NOTE: if you wish to test expiry, wait 15 minutes): ")
    print("Attempting to write expenses as RobertL.")
    r = requests.post("http://127.0.0.1:2250/add_expense", data={'username': 'RobertL', 'password': user_pw, 'code': '', 'token': user_token, 'expense': 'At least 50 marks on SENG2250, please'})
    print(r.text)
    if 'Incorrect token' in r.text:
        r = requests.post("http://127.0.0.1:2250/admin_console/remove_user", data={'username': username, 'password': password, 'code': '', 'token': '', 'userToRemove': 'RobertL'})
        os.remove("data/auth.txt")
        os.remove("data/tokens.txt")
        print("Exiting program.")
        exit()
    print("Attempting to view meeting minutes as RobertL [should not be given access]")
    r = requests.post("http://127.0.0.1:2250/view_meeting_minutes", data={'username': 'RobertL', 'password': user_pw, 'code': code, 'token': user_token})
    print(r.text)
    print("Testing RobertL's admin permissions [should not be given access]")
    r = requests.post("http://127.0.0.1:2250/admin_console/add_user", data={'username': 'RobertL', 'password': user_pw, 'code': code, 'token': user_token, 'newUser': ['WillH', 'seng2250a@gmail.com', 2]})
    print(r.text)

    ## Testing Secret level access
    print("Changing RobertL's level to Secret")
    r = requests.post("http://127.0.0.1:2250/admin_console/modify_user", data={'username': username, 'password': password, 'code': code, 'token': user_token, 'userToModify': 'RobertL', 'newSecLevel': '2'})
    print(r.text)
    print("Attempting to write expenses as RobertL [should be denied access]")
    r = requests.post("http://127.0.0.1:2250/add_expense", data={'username': 'RobertL', 'password': user_pw, 'code': '', 'token': user_token, 'expense': 'THIS EXPENSE SHOULD NOT BE WRITTEN'})
    print(r.text)
    print("Attempting to view meeting minutes as RobertL [should have access as Secret]")
    r = requests.post("http://127.0.0.1:2250/view_meeting_minutes", data={'username': 'RobertL', 'password': user_pw, 'code': code, 'token': user_token})
    print(r.text)
    print("Attempting to add meeting minutes as RobertL [should have access as Secret]")
    r = requests.post("http://127.0.0.1:2250/add_meeting_minutes", data={'username': 'RobertL', 'password': user_pw, 'code': code, 'token': user_token, 'minutes': 'Implemented meeting minutes into Mako'})
    print(r.text)

    ## Testing Unclassified level access
    print("Changing RobertL's level to Unclassified")
    r = requests.post("http://127.0.0.1:2250/admin_console/modify_user", data={'username': username, 'password': password, 'code': code, 'token': user_token, 'userToModify': 'RobertL', 'newSecLevel': '1'})
    print(r.text)
    print("Attempting to add meeting minutes as RobertL [should not be given access]")
    r = requests.post("http://127.0.0.1:2250/add_meeting_minutes", data={'username': 'RobertL', 'password': user_pw, 'code': code, 'token': user_token, 'minutes': 'SHOULD NOT BE WRITTEN'})
    print(r.text)
    print("Attempting to view expenses as RobertL [should have access as Unclassified]")
    r = requests.post("http://127.0.0.1:2250/audit_expenses", data={'username': 'RobertL', 'password': user_pw, 'code': code, 'token': user_token})
    print(r.text)
    print("Attempting to add shift as RobertL [should have access as Unclassified]")
    r = requests.post("http://127.0.0.1:2250/roster_shift", data={'username': 'RobertL', 'password': user_pw, 'code': code, 'token': user_token, 'shift': 'Robert L. - 15:00 to 21:00'})
    print(r.text)
    print("Attempting to view shifts as RobertL [should have access as Unclassified]")
    r = requests.post("http://127.0.0.1:2250/view_roster", data={'username': 'RobertL', 'password': user_pw, 'code': code, 'token': user_token})
    print(r.text)
    print("Removing user RobertL")
    r = requests.post("http://127.0.0.1:2250/admin_console/remove_user", data={'username': username, 'password': password, 'code': '', 'token': '', 'userToRemove': 'RobertL'})
    print(r.text)

    os.remove("data/auth.txt")
    os.remove("data/tokens.txt")
    print("Testing complete!")
    exit()
