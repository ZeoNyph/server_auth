import requests, getpass


if __name__ == "__main__":
    """ # The following shows example code requesting each of the example functions from the server
    r = requests.get("http://127.0.0.1:2250/")
    # server responses are given in the text variable shown with the following
    print(r.text)

    r = requests.post("http://127.0.0.1:2250/hello", data={"name": "Alice"})
    print(r.text)

    r = requests.post("http://127.0.0.1:2250/hello")
    print(r.text)

    r = requests.get("http://127.0.0.1:2250/redirect")
    print(r.text)

    r = requests.get("http://127.0.0.1:2250/visitors?name=Frank")
    print(r.text)

    # For some error checking, you can also check whether a request was successful by looking at the status_code
    # variable
    r = requests.get("http://127.0.0.1:2250/lost_page")
    print(r.status_code)
    if r.status_code == 404:
        print("The page was not found")

    # For more complicated responses, e.g. when the server returns a dictionary, you can use the json() method
    # to process as a dictionary
    r = requests.get("http://127.0.0.1:2250/json")
    print(r.json()) """

    ### START CLIENT
    username = input("What username would you like to use?")
    choice = input("Would you like to use an MFA token if you have one? [y/n]")
    token = ''
    if choice[0].lower() == 'y':
        token = input("What is the MFA token? (this should be in your email inbox):")
    password = getpass.getpass("What is the password assigned to this user?")
    code = getpass.getpass("If you have an MFA code for authentication, please add it here, or just hit Enter if not:")

    ## test admin console
    r = requests.post("http://127.0.0.1:2250/admin_console/add_user", data={'username': username, 'password': password, 'code': code, 'token': token, 'newUser': ['RobertL', 'mithunsivanesan@gmail.com', 3]})
    print(r.text)
    if r.text == 'Access granted':
        pass
    else:
        print("This user does not have access to the admin console, skipping admin tests")