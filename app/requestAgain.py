"""
    sends text/email to all patients who haven't posted google review yet 
"""
import requests
import json

import smtplib
import hyperlink
from twilio.rest import Client
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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


# """fetch patients from db that haven't written a google review"""
DB_URL = 'http://127.0.0.1:5000/requestAgain'

res_json = requests.get(DB_URL).text
res = json.loads(res_json)



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

def main():
    
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(EMAIL, PASSWORD)
    
    url = hyperlink.parse(LINK_GOOGLE_BUSINESS)
    better_url = url.replace(scheme=u'https', port=443)
    
    # iterate through each patient, send request mail/text
    for patient in res["patients"]:
        if not patient["wrote_review"]:
            first_name = patient["name"].split()[0]
            email = patient["email"]
            text = patient["phone"]

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
          
    smtpObj.quit()

    
if __name__ == '__main__':
    main()
    
