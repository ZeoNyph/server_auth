"""
File: server.py
Author: Mithun Sivanesan, C3403606
Desc: This file contains the server implementation for A3.
"""

#imports
import os, smtplib, ssl, hashlib, string, random, time
from user import User
from dotenv import load_dotenv
from flask import Flask, request, redirect, url_for

#global vars
app = Flask(__name__)
users = []
load_dotenv("mailgun.env") #loads Mailgun API Key and SMTP password; placed into .env file for security with GitHub/Git

"""
Adds user to portal. Requires admin access.
"""
@app.route("/admin_console/add_user", methods=["POST"])
def admin_add_user():
    # login 
    status = user_login(request.form.get('username'), request.form.get('password'), request.form.get('code'), request.form.get('token'))
    if status != 0 and status != 5: #if failure
        return send_error_msg(status)
    user = get_user(request.form.get('username'))
    if user.get_secLevel() < 4: #if not having access
        return send_error_msg(status) + "\nAccess denied"
    if not request.form.getlist('newUser'): #if missing param
        return send_error_msg(status) + '\nMissing new user information'
    info = request.form.getlist('newUser')
    if get_user(info[0]): #if 'new' user exists
        return send_error_msg(status) + '\nUser already exists'
    file = open("data/users.txt", 'a')
    new_user = User(info[0], info[1], int(info[2]))
    send_acc_mail(info[1], new_user.create_pw(), info[0])
    users.append(new_user)
    file.write(f"{info[0]}, {info[1]}, {new_user.get_secLevel()}, {new_user.get_pw_hash()}\n")
    file.close()
    return send_error_msg(status) + "\nUser added."   
        
"""
Remove user from portal, requires admin access
"""
@app.route("/admin_console/remove_user", methods=["POST"])
def admin_remove_user():
    status = user_login(request.form.get('username'), request.form.get('password'), request.form.get('code'), request.form.get('token'))
    if status != 0 and status != 5:
        return send_error_msg(status)
    user = get_user(request.form.get('username'))
    if user.get_secLevel() < 4:
        return send_error_msg(status) + "\nAccess denied"
    if not request.form.get('userToRemove'):
        return send_error_msg(status) + "\nMissing user to remove"
    if not get_user(request.form.get('userToRemove')):
        return send_error_msg(status) + '\nUser does not exist, cannot remove'
    with open("data/users.txt","r+") as f:
        new_f = f.readlines()
        f.seek(0)
        for line in new_f:
            if request.form['userToRemove']not in line:
                f.write(line)
            else:
                users.remove(get_user(request.form.get('userToRemove')))
        f.truncate()
    return send_error_msg(status) + '\nUser removed.'

"""
Modifies the security level of the user, requires admin access
"""
@app.route("/admin_console/modify_user", methods=["POST"])
def admin_modify_user():
    status = user_login(request.form.get('username'), request.form.get('password'), request.form.get('code'), request.form.get('token'))
    if status != 0 and status != 5:
        return send_error_msg(status)
    user = get_user(request.form.get('username'))
    if user.get_secLevel() < 4:
        return send_error_msg(status) + "\nAccess denied"
    if not request.form.get('userToModify'):
        return send_error_msg(status) + "\nMissing user to remove"
    if not request.form.get('newSecLevel'):
        return send_error_msg(status) + "\nMissing security level"
    with open("data/users.txt","r+") as f:
        new_f = f.readlines()
        f.seek(0)
        for line in new_f:
            if request.form.get('userToModify') in line:
                info = line.split(", ")
                info[2] = request.form.get('newSecLevel')
                line = ', '.join(info)
                get_user(request.form.get('userToModify')).set_secLevel(int(info[2]))
            f.write(line)
        f.truncate()
    get_user(request.form.get('userToModify')).set_secLevel(int(request.form.get('newSecLevel')))
    return send_error_msg(status) + "\nUser modified."  

# Services

@app.route("/audit_expenses", methods=["POST"])
def audit_expenses():
    status = user_login(request.form.get('username'), request.form.get('password'), request.form.get('code'), request.form.get('token'))
    if status != 0 and status != 5:
        return send_error_msg(status)
    user = get_user(request.form.get('username'))
    if user.get_secLevel() > 4:
        return send_error_msg(status) + "\nAccess denied"
    if os.path.exists("data/expenses.txt"):
        with open("data/expenses.txt", 'r') as f:
            return f.read()
    return "No expenses yet"


@app.route("/add_expense", methods=["POST"])
def add_expense():
    status = user_login(request.form.get('username'), request.form.get('password'), request.form.get('code'), request.form.get('token'))
    if status != 0 and status != 5:
        return send_error_msg(status)
    user = get_user(request.form.get('username'))
    if user.get_secLevel() < 3:
        return send_error_msg(status) + "\nAccess denied"
    if request.form:
        with open("data/expenses.txt", 'a') as f:
            f.write(request.form.get('expense'))
        return "Expense added"
    return "No expense was given"


@app.route("/audit_timesheets", methods=["POST"])
def audit_timesheets():
    status = user_login(request.form.get('username'), request.form.get('password'), request.form.get('code'), request.form.get('token'))
    if status != 0 and status != 5:
        return send_error_msg(status)
    user = get_user(request.form.get('username'))
    if user.get_secLevel() > 4:
        return send_error_msg(status) + "\nAccess denied"
    if os.path.exists("data/timesheets.txt"):
        with open("data/timesheets.txt", 'r') as f:
            return f.read()
    return "No timesheets yet"


@app.route("/submit_timesheet", methods=["POST"])
def submit_timesheet():
    status = user_login(request.form.get('username'), request.form.get('password'), request.form.get('code'), request.form.get('token'))
    if status != 0 and status != 5:
        return send_error_msg(status)
    user = get_user(request.form.get('username'))
    if user.get_secLevel() < 3:
        return send_error_msg(status) + "\nAccess denied"
    if request.form:
        with open("data/timesheets.txt", 'a') as f:
            f.write(request.form.get('timesheet'))
        return "Timesheet added"
    return "No timesheet was given"


@app.route("/view_meeting_minutes", methods=["POST"])
def view_meeting_minutes():
    status = user_login(request.form.get('username'), request.form.get('password'), request.form.get('code'), request.form.get('token'))
    if status != 0 and status != 5:
        return send_error_msg(status)
    user = get_user(request.form.get('username'))
    if user.get_secLevel() > 2:
        return send_error_msg(status) + "\nAccess denied"
    if os.path.exists("data/meeting_minutes.txt"):
        with open("data/meeting_minutes.txt", 'r') as f:
            return f.read()
    return "No meeting minutes yet"


@app.route("/add_meeting_minutes", methods=["POST"])
def add_meeting_minutes():
    status = user_login(request.form.get('username'), request.form.get('password'), request.form.get('code'), request.form.get('token'))
    if status != 0 and status != 5:
        return send_error_msg(status)
    user = get_user(request.form.get('username'))
    if user.get_secLevel() < 2:
        return send_error_msg(status) + "\nAccess denied"
    if request.form:
        with open("data/meeting_minutes.txt", 'a') as f:
            f.write(request.form.get('minutes'))
        return "Meeting minutes added"
    return "No meeting minutes given"


@app.route("/view_roster", methods=["POST"])
def view_roster():
    status = user_login(request.form.get('username'), request.form.get('password'), request.form.get('code'), request.form.get('token'))
    if status != 0 and status != 5:
        return send_error_msg(status)
    user = get_user(request.form.get('username'))
    if user.get_secLevel() > 1:
        return send_error_msg(status) + "\nAccess denied"
    if os.path.exists("data/roster.txt"):
        with open("data/roster.txt", 'r') as f:
            return f.read()
    return "No roster yet"


@app.route("/roster_shift", methods=["POST"])
def roster_shift():
    status = user_login(request.form.get('username'), request.form.get('password'), request.form.get('code'), request.form.get('token'))
    if status != 0 and status != 5:
        return send_error_msg(status)
    user = get_user(request.form.get('username'))
    if user.get_secLevel() < 1:
        return send_error_msg(status) + "\nAccess denied"
    if request.form:
        with open("data/roster.txt", 'a') as f:
            f.write(request.form.get('shift'))
        return "Shift rostered"
    return "No shift given"

# Server functions

"""
Initializes server's user repository.
"""
def user_init():
    if os.path.exists("data/users.txt"):
        file = open('data/users.txt', 'r')
        for user in file:
            user_info = user.removesuffix("\n").split(", ")
            users.append(User(user_info[0], user_info[1], int(user_info[2]), user_info[3]))
        file.close()
    else: # create new root user if no users.txt detected
        root_user = User("root", "seng2250a@gmail.com", 4)
        print(f"Here is the root user password (This will not be displayed again, unless users.txt is deleted): {root_user.create_pw()}")
        users.append(root_user)
        file = open("data/users.txt", "a")
        file.write(f"{root_user.get_name()}, {root_user.get_email()}, {root_user.get_secLevel()}, {root_user.get_pw_hash()}\n")
        file.close()

## Mailing methods
def send_acc_mail(email_addr: str, user_pw: str, username: str):
    port = 465
    password = os.getenv('MAILGUN_PW')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.mailgun.org", port, context=context) as serv:
        serv.login("postmaster@sandboxd683e7443cd54af0b39fa547c1c51695.mailgun.org", password=password)
        message = f"""\
Subject: Your account details for Mako

Hi, {username}.
Here are your details for the Mako portal:
Username: {username} 
Password: {user_pw}"""
        serv.sendmail("admin@mako.com", email_addr, message)

def send_token_mail(email_addr: str, user_token: str, username: str):
    port = 465
    password = os.getenv('MAILGUN_PW')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.mailgun.org", port, context=context) as serv:
        serv.login("postmaster@sandboxd683e7443cd54af0b39fa547c1c51695.mailgun.org", password=password)
        message = f"""\
Subject: Your MFA token for Mako

Hi, {username}.
Here is your MFA (Multi-Factor Authentication) token for Mako. Note that this is only valid for 15 minutes:
Token: {user_token}"""
        serv.sendmail("admin@mako.com", email_addr, message)

def send_MFA_mail(email_addr: str, code: str, username: str):
    port = 465
    password = os.getenv('MAILGUN_PW')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.mailgun.org", port, context=context) as serv:
        serv.login("postmaster@sandboxd683e7443cd54af0b39fa547c1c51695.mailgun.org", password=password)
        message = f"""\
Subject: Your MFA code for Mako

Hi, {username}.
Here is your MFA (Multi-Factor Authentication) code for Mako, use this for verification:
Code: {code}"""
        serv.sendmail("admin@mako.com", email_addr, message)

"""
Creates a new token for given user.
"""
def create_new_token(user: User):
    token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20))
    t_exp = time.time() + (15*60)
    file = open('data/tokens.txt', 'a')
    file.write(f"{user.get_name()}, {token}, {t_exp}\n")
    send_token_mail(user.get_email(), token, user.get_name())
    file.close()

"""
Validates a token for given user
"""
def validate_token(username: str, token='') -> bool:
    isValid = False
    if os.path.exists("data/tokens.txt"):
        file = open("data/tokens.txt", "r+")
        for user in file:
            info = user.removesuffix("\n").split(", ")
            if username == info[0] and token == info[1] and float(info[2]) > time.time():
                isValid = True
                file.close()
                break
            elif float(info[2]) < time.time() and len(info) == 3:
                info.append("EXPIRED")
                user = ', '.join(info)
    return isValid

"""
Checks if user has a MFA code stored
"""
def validate_mfa(username: str) -> bool:
    isValid = False
    if os.path.exists("data/auth.txt"):
        file = open("data/auth.txt", "r")
        for user in file:
            info = user.removesuffix("\n").split(", ")
            if username == info[0]:
                isValid = True
                file.close()
                break
    return isValid
    
"""
Generates a code for MFA
"""
def mfa_codegen() -> int:
    randomgen = random.SystemRandom()
    return random.SystemRandom.randint(randomgen, 100000,999999)

"""
Main code for MFA; creates code and sends to user
"""
def mfa(user: User):
    file = open("data/auth.txt", 'a')
    code = mfa_codegen()
    file.write(f"{user.get_name()}, {code}\n")
    file.close()
    send_MFA_mail(user.get_email(), code, user.get_name())

"""
Verifies MFA code
"""
def mfa_verify(username: str, code: int) -> bool:
    isValid = False
    if os.path.exists("data/auth.txt"):
        file = open("data/auth.txt", "r")
        for user in file:
            info = user.removesuffix("\n").split(", ")
            if info[0] == username and info[1] == code:
                isValid = True
                file.close()
                break
    return isValid

"""
Gets user from list.
"""
def get_user(username: str) -> User:
    for user in users:
        if username == user.get_name():
            return user
    return None


"""
Logs in user.

Error codes:
0: successful login
1: user does not exist
2: incorrect password
3: MFA required
4: incorrect MFA code
5: successful login, but token now required in future logins
6: incorrect token
"""
def user_login(username: str, password: str, code='', token='') -> int:
    user = get_user(username)
    if user == None:
        return 1
    if user.get_pw_hash() != password:
        return 2
    if not validate_mfa(username) and code == '' and username != "root":
        mfa(user)
        return 3
    if not mfa_verify(username, code) and not validate_token(username, token) and code != '' and username != 'root':
        return 4
    elif mfa_verify(username, code) and not validate_token(username, token) and code != '' and username != 'root':
        create_new_token(user)
        return 5
    if not validate_token(username, token) and username != 'root':
        return 6
    return 0


"""
Returns an error message based on login status. 
"""
def send_error_msg(status: int) -> str:
    match status:
        case 0:
            return 'Login successful.'
        case 1:
            return 'User does not exist'
        case 2:
            return 'Incorrect password.'
        case 3:
            return 'MFA required, send MFA code from email on next login attempt'
        case 4:
            return 'Incorrect MFA code'
        case 5:
            return 'Login successful. Use token next time for future logins until expiry'
        case 6:
            return 'Incorrect token'
        case _:
            return 'Unknown status'


if __name__ == "__main__":
    os.makedirs("data/", exist_ok=True)
    user_init()
    app.run(host="127.0.0.1", port="2250")