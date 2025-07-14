import pandas as pd
import numpy as np
from pandas.api.types import is_number
from dotenv import load_dotenv
import smtplib
import os
from email.message import EmailMessage

#function to change numeric values to float64 and leave non numeric values unchange
def convert_float(x):
    try:
        x.astype('float64')
        return x
    except:
        return x

#function to change numeric values to float64 and leave non numeric values unchange
def convert_int(x):
    try:
        x.astype('int64')
        return x
    except:
        return x

#enforce datetime data type for valid dates and leave invalid dates unchanged
def convert_date(x):
    try:
        pd.to_datetime(x)
        return x
    except:
        return x
    
#date comparison
def compare_date(x, y):
    try:
        return x <= y
    except:
        return False
    
#quantity is in valid range
#use '&' and '|' logical operators as these have been overloaded from the bitwise operators to element wise operators in pandas
#if using python 'and' 'or' it will perform the operation object wise
#wrap in '()' as bitwise operators in python have lower precedence than comparison operators and will execute the '&' too early
def quant_range(x, y):
    try:
        return (abs(x) <= y) & (np.dtype(type(x)) == 'int64') & (x != 0)
    except:
        return False
    
#validation check for the contract year 
#the year must be a number data type and this year or a future year
def is_valid_contract_yr(y, cy):
    try:
       return (is_number(y)) & (y >= cy)
    except:
        return False
    

#validation check for the strike price
#must be a numeric data type and must also be populated for options
#since checking for a single scalar value, use native python 'in' instead of pandas 'isin' as it will check the entire df
def is_valid_strike(strike, contract_type):
    try:
        if contract_type in ['C', 'P']:
            return (is_number(strike)) & (strike != 0) & (strike != float('NaN'))
        elif contract_type == 'F':
            return True
        else:
            return False
    except:
        #can be blank if a future
        return False
    
#pandas to_numeric is deprecating the 'ignore' option for errors which leaves the value unchanged
#behavior replicating 
def safe_to_numeric(val):
    try:
        return pd.to_numeric(val)
    except (ValueError, TypeError):
        return val
    
# email function
# using the email and smtp module with the EmailMessage class to send email with attachment
def send_email(filepath, log_path, email_body):

    # create a multipart message
    load_dotenv() # this loads the variables from '.env' into the environment
    msg = EmailMessage()
    msg['From'] = os.getenv('SENDER_EMAIL')
    msg['To'] = os.getenv('RECEIVER_EMAIL')
    msg['Subject'] = 'Data Validation Report'

    # email body
    msg.set_content(email_body)

    # add the excel attachment
    with open(filepath, 'rb') as file:
        file_data = file.read()
        file_name = os.path.basename(filepath) # extract the name of the file
        msg.add_attachment(file_data, maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=file_name)

    # add the log file
    with open(log_path, 'rb') as log_file:
        log_data = log_file.read()
        log_name = os.path.basename(log_path) # extract the name of the file
        msg.add_attachment(log_data, maintype='text', subtype='plain', filename=log_name)
    
    # send email 
    try:
        # set up the server connection using SMTP
        # server and port 
        smtp_server = os.getenv('SMTP_SERVER')
        port = int(os.getenv('PORT')) # must be an int

        with smtplib.SMTP(smtp_server, port) as server:
            # start communication with EHLO/HELO
            code, message = server.ehlo()

            #this will put the SMTP connection in TLS so that all commands will be encrypted
            server.starttls()
            code, message = server.ehlo()
            print(f'EHLO: Status Code: {code}, Message: {message.decode()}')
            
            # perform login 
            username = os.getenv('SENDER_EMAIL')
            email_pass = os.getenv("EMAIL_PASSWORD")
            response = server.login(username, email_pass)
            print(f'LOGIN: {response}')

            # send the email and capture status
            server.send_message(msg)
            print('Email sent successfully with SMTP.')
            
    except Exception as e:
        print(f'An error occurred: {e}')
        return False

    return True



