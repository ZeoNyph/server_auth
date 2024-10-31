# README: SENG2250 A3

Written by: Mithun Sivanesan, C3403606

This is the source code for Assessment 3 of SENG2250 (System and Network Security).

## Requirements

Flask, Requests, python-dotenv

## Instructions

- Install the requirements using:
```sh
python -m pip install -r requirements.txt
```
- Run the server using:
```sh
python server.py
```
- Run the client program using:
```sh
python client.py
```
## Additional Notes
- The Mailgun API key and SMTP password are stored as environment variables in mailgun.env; if needed, feel free to put them directly into the code.
- This assessment also does not check for incorrect inputs ('sunny day' scenario), so please make sure the inputs are correct.
