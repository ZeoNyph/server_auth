"""
This is our HTTP server, to run, just install Flask using the pip tool and run this file with `python server.py`.
In this, we provide some example functions showing what Flask can do, then the functions you should add authentication
and access control to.
"""

import os, smtplib, ssl, hashlib, string, random, time
from user import User
from dotenv import load_dotenv
from flask import Flask, request, redirect, url_for
app = Flask(__name__)
users = []

load_dotenv("mailgun.env")


#### Example functions
# The following are examples of what you can do with Flask, you will probably want remove them on submission

@app.route("/")
def hello_world():
    """
    This function runs when the url http://<host>:<port>/ is requested,
    sub-urls can be specified but putting different arguments into @app.route(args).
    The return value is sent over the network to the client.
    """
    return "Hello, World!"


@app.route("/hello", methods=["POST"])
def post_hello():
    """
    This shows an example of a post request, one of the types of http message.
    This allows a client to send information inside the payload part of the http
    packet, and the server can read that information in the form of the dictionary
    `request.form`.
    You can also do similar with GET requests, although the dictionary
    will then be `request.args`. Additionally, the data will be directly in the url,
    so you likely want to avoid GET if sending sensitive information such as passwords
    as we are in this assignment.
    """
    if request.form.get("name"):
        return f"Hello {request.form['name']}"
    return "Hello stranger"


@app.route("/redirect")
def move_to_hello_name():
    """
    With this, we show how to redirect a client to a different url that we provide.
    """
    return redirect(url_for("hello", name="Bob"))


@app.route("/hello/<name>")
def hello(name):
    """
    For this, we show how to use information in the url as an argument to the function.
    The contents of the angle brackets in the route are the name of variable gains the value
    of what the client enters in it place. E.g. if the client requests `http://127.0.0.1:2250/hello/charlie`
    then name = "charlie".
    """
    return f"Hello {name}"


@app.route("/visitors", methods=["GET"])
def visitor_list():
    """
    Since this is an http server, it is stateless, allowing it handle many clients simultaneously, but also
    meaning we can not directly track users as they progress through the app.
    So, instead to keep information in any long term basis, we need to save to external service, such as a file.
    Note that using a file is in reality bad practice, but it is convenient for this assignment.
    """
    # First we append the new visitor to the list
    with open("data/visitors.txt", 'a') as f:
        f.write(request.args['name'] if request.args.get("name") else "stranger")
        f.write("\n")
    # Then we send back the list
    with open("data/visitors.txt", 'r') as f:
        return f.read()


@app.route("/json")
def json_data():
    """
    With this, we demonstrate how more complex data can be returned as a dictionary, specifically,
    it gets translated into a json file and sent back to the client. You can also send back lists this way.
    """
    return {"data": "hello", "numbers": [1, 2, 3]}

#### End example functions


@app.route("/admin_console", methods=["POST"])
def admin_console():
    if request.form.get("username") and request.form.get("password"):
        isGivenAccess = False
        for user in users:
            if user.get_name() == request.form['username'] and user.get_pw_hash() == hashlib.sha256(request.form['password'].encode()).hexdigest() and int(user.get_secLevel()) == 4:
                isGivenAccess = True
                return "Access granted"
        if not isGivenAccess:
            return "Access denied"
    else:
        return "Missing inputs."



@app.route("/audit_expenses", methods=["POST"])
def audit_expenses():
    if os.path.exists("data/expenses.txt"):
        with open("data/expenses.txt", 'r') as f:
            return f.read()
    return "No expenses yet"


@app.route("/add_expense", methods=["POST"])
def add_expense():
    if request.form:
        with open("data/expenses.txt", 'a') as f:
            f.write(request.form)
        return "Expense added"
    return "No expense was given"


@app.route("/audit_timesheets", methods=["POST"])
def audit_timesheets():
    if os.path.exists("data/timesheets.txt"):
        with open("data/timesheets.txt", 'r') as f:
            return f.read()
    return "No timesheets yet"


@app.route("/submit_timesheet", methods=["POST"])
def submit_timesheet():
    if request.form:
        with open("data/timesheets.txt", 'a') as f:
            f.write(request.form)
        return "Timesheet added"
    return "No timesheet was given"


@app.route("/view_meeting_minutes", methods=["POST"])
def view_meeting_minutes():
    if os.path.exists("data/meeting_minutes.txt"):
        with open("data/meeting_minutes.txt", 'r') as f:
            return f.read()
    return "No meeting minutes yet"


@app.route("/add_meeting_minutes", methods=["POST"])
def add_meeting_minutes():
    if os.path.exists("data/meeting_minutes.txt"):
        with open("data/meeting_minutes.txt", 'r') as f:
            f.write(request.form)
        return "Meeting minutes added"
    return "No meeting minutes given"


@app.route("/view_roster", methods=["POST"])
def view_roster():
    if os.path.exists("data/roster.txt"):
        with open("data/roster.txt", 'r') as f:
            return f.read()
    return "No roster yet"


@app.route("/roster_shift", methods=["POST"])
def roster_shift():
    if os.path.exists("data/roster.txt"):
        with open("data/roster.txt", 'r') as f:
            f.write(request.form)
        return "Shift rostered"
    return "No shift given"

def user_init():
    if os.path.exists("data/users.txt"):
        file = open('data/users.txt', 'r')
        for user in file:
            user_info = user.split(", ")
            users.append(User(user_info[0], user_info[1], int(user_info[2]), user_info[3]))
        file.close()
    else:
        root_user = User("root", "root@SENG2250.uon.edu.au", 4)
        print(f"Here is the root user password (This will not be displayed again, unless users.txt is deleted): {root_user.create_pw()}")
        users.append(root_user)
        file = open("data/users.txt", "a")
        file.write(f"{root_user.get_name()}, {root_user.get_email()}, {root_user.get_secLevel()}, {root_user.get_pw_hash()}")
        file.close()

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
        serv.sendmail("admin.mako@SENG2250.uon.edu.au", email_addr, message)

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
        serv.sendmail("admin.mako@SENG2250.uon.edu.au", email_addr, message)

def send_MFA_mail(email_addr: str, code: str, username: str):
    port = 465
    password = os.getenv('MAILGUN_PW')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.mailgun.org", port, context=context) as serv:
        serv.login("postmaster@sandboxd683e7443cd54af0b39fa547c1c51695.mailgun.org", password=password)
        message = f"""\
Subject: Your MFA token for Mako

Hi, {username}.
Here is your MFA (Multi-Factor Authentication) code for Mako, use this for verification:
Token: {code}"""
        serv.sendmail("admin.mako@SENG2250.uon.edu.au", email_addr, message)

def create_new_token(user: User):
    token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20))
    t_exp = time.time() + (15*60)
    file = open('data/tokens.txt', 'a')
    file.write(f"{user.get_name()}, {token}, {t_exp}")
    send_token_mail(user.get_email(), token, user.get_name())
    file.close()

def validate_token(username: str, token: str) -> bool:
    isValid = False
    if os.path.exists("data/tokens.txt"):
        file = open("data/tokens.txt", "r")
        for user in file:
            info = user.split(", ")
            if username == info[0] and token == info[1] and int(info[2]) > time.time():
                isValid = True
                file.close()
                break
    return isValid
    
def mfa_codegen() -> int:
    return random.SystemRandom.randint(100000,999999)

def mfa(user: User):
    file = open("data/auth.txt", 'a')
    code = mfa_codegen()
    file.write(f"{user.get_name()}, {code}")
    file.close()
    send_MFA_mail(user.get_email(), code, user.get_name())


def mfa_verify(username: str, code: int) -> bool:
    isValid = False
    if os.path.exists("data/auth.txt"):
        file = open("data/auth.txt", "a")
        for user in file:
            info = user.split(", ")
            if info[0] == username and int(info[1]) == code:
                isValid = True
                break
    return isValid


def get_user(username: str) -> User:
    for user in users:
        if username == user.get_name():
            return user
    return None



if __name__ == "__main__":
    os.makedirs("data/", exist_ok=True)
    user_init()
    app.run(host="127.0.0.1", port="2250")