# README

Written by: Mithun Sivanesan, C3403606

This is the source code for Assessment 3 of SENG2250 (System and Network Security). It is an implementation of server authentication, as well as multi-factor authentication using Mailgun as a host for SMTP, and Flask for creating a demo server.

## Requirements

Flask, Requests, python-dotenv

## Instructions

Install the requirements using:
```sh
python -m pip install -r requirements.txt
```
Run the server using:
```sh
python server.py
```
Run the client program using:
```sh
python client.py
```
Follow the instructions given on the client terminal, inputting information where necessary.

## Additional Notes
- The Mailgun API key and SMTP password are stored as environment variables in mailgun.env; you will need to add your own.
- This assessment also does not check for incorrect inputs ('sunny day' scenario), so please make sure the inputs are correct.
- Do not worry if it looks like nothing is being typed into the password, token, and code fields; inputs are hidden for security purposes (like entering password for sudo commands in Linux terminals)
