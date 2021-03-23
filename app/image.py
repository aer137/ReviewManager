import openpyxl
import smtplib
import hyperlink
from twilio.rest import Client
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import json
import requests
import sys

# ------------ EDIT BELOW ----------------

BUSINESS_NAME = ''
EMAIL = ''
PASSWORD = '' # for email
LINK_GOOGLE_BUSINESS = ''
EMAIL_SUBJECT = ''
TWILIO_SID = ''
TWILIO_TOKEN = ''
IMAGE_SOURCE = ''
RATE_US = ''  # link to google review
TWILIO_PHONE_NUMBER = ''

#  --------------------------------------

SPREADNAME = sys.argv[1]
DB_URL = 'http://127.0.0.1:5000/patients'


def nmbr_verter(t):
    text = str(t)
    if len(text) == 12 and text[0] == '+':
        return t
    s = ''
    if text[0] != '+':
        txt = []
        txt.append('+')
    for i in text:
        if ord(i) >= ord('0') and ord(i) <= ord('9'):
            txt.append(i)
    if len(txt) != 12:
        txt.insert(1, '1')
    return s.join(txt)

def send(SPREADNAME):
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(EMAIL, PASSWORD)
    
    wb = openpyxl.load_workbook(SPREADNAME)
    sheet = wb['Sheet1']
    end = sheet.max_row
    N = 6  # number of total columns
    FN = 0 # first name column

    # for adding patient to db
    patient_names = set()
    f = open('../server/worker/excels_documented.txt', 'a+')
    already_scraped = set(line.rstrip('\n') for line in f)
    scraped = set()
    patient_objs = []

    url = hyperlink.parse(LINK_GOOGLE_BUSINESS)

    better_url = url.replace(scheme=u'https', port=443)

    # iterate through each client, send request mail/text if they were happy
    for i in range (1, end):
            if sheet[i][N-1].value == 'yes' or sheet[i][N-1].value == 'Yes' or sheet[i][N-1].value == 'YES':
                # print(sheet[i][FN].value + ' = first name')
                first_name = sheet[i][FN].value
                first_name = getNickname(first_name)
                # print(sheet[i][N-2].value + ' = email')
                email = sheet[i][N-2].value
                # print(sheet[i][2].value)
                text = sheet[i][2].value

                html_message = """\
                <html>
                    <head></head>
                    <body>
                        <p style="color:#2c7d23">Hi {first_name}!<br><br>
                        Please take 10 seconds and <a href={RATE_US}>rate us</a>!<br><br>
                        THANK YOU FROM THE TEAM AT {BUSINESS_NAME}!<br><br>
                        <img src = {IMAGE_SOURCE}>
                    </body>
                    </html>
                """.format(first_name = first_name)
                
                msg = MIMEMultipart('alternative')
                msg['Subject'] = EMAIL_SUBJECT
                msg['From'] = EMAIL
                
                html = MIMEText(html_message, 'html')
                msg.attach(html)
                smtpObj.sendmail(EMAIL, email, msg.as_string())

                # text message version
                if text: 
                    msg = 'Hi ' + first_name + '!\n\nPlease take 10 seconds and rate us!\n\n' + RATE_US + '\n\nTHANK YOU FROM THE TEAM AT ' + BUSINESS_NAME
                    account_sid = TWILIO_SID
                    auth_token = TWILIO_TOKEN
                    pic = IMAGE_SOURCE
                    nmbr = nmbr_verter(text)
                    client = Client(account_sid, auth_token)
                    message = client.messages \
                                    .create(
                                         body=msg,
                                         media_url=[pic],
                                         from_= TWILIO_PHONE_NUMBER,
                                         to=nmbr
                                    )

                # add patient to db
                first, last, email_addr, phone_num = 0, 1, 2, 4
                first_name, last_name, email_address, phone_number = getPatientInfo(i, sheet, first, last, email_addr, phone_num)
                # generate patient object
                if last_name is not None:
                    patient_name = first_name + ' ' + last_name
                else:
                    patient_name = first_name
                if patient_name not in patient_names:
                    patient_names.add(patient_name)
                    patient = generatePatientObj(patient_name, SPREADNAME, phone_number, email_address)
                    r = requests.post(DB_URL, json=patient)



    scraped.add(SPREADNAME)
    # add scraped to already_scraped
    f.write('\n'.join(str(p) for p in scraped))
    f.close()      
    smtpObj.quit()

def generatePatientObj(name, sheet, phone, email):
    return {
        'name': name,
        'excel_sheet' : sheet,
        'phone' : phone,
        'email' : email,
        'wrote_review' : 0,
        'name_on_google' : ""
    }

def getPatientInfo(i, sheet, first, last, email, phone):
    first_name = sheet[i][first].value
    last_name = sheet[i][last].value
    email_address = sheet[i][email].value
    phone_number = sheet[i][phone].value
    return first_name, last_name, email_address, phone_number

def getNickname(firstName):
    if "\'" in firstName or "\'" in firstName:
        firstName = firstName.split()[1].replace("\'", '').replace("\"", '')
    return firstName



send(SPREADNAME)