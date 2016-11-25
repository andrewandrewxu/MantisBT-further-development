#! /usr/bin/python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback

def sendMail(to, subject, content, attachment):
    SMTPserver = 'smtp.163.com'
    sender = 'palmwin_test@163.com'

    # Email headers
    msg = MIMEMultipart()
    text = MIMEText(content)
    msg.attach(text)
    msg['Subject'] = subject
    msg['from'] = sender
    msg['To'] = ",".join(to)

    # Email attachment
    if attachment:
        file = open(attachment, 'rb')
        att = MIMEText(file.read(), 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        att["Content-Disposition"] = 'attachment; filename="bug2case.csv"'
        msg.attach(att)

    # Email Sending
    mailserver = smtplib.SMTP(SMTPserver, 25)
    mailserver.login(sender, password = 'handwin11g')
    try:
        mailserver.sendmail(sender, to, msg.as_string())
    except smtplib.SMTPException, e:
        exstr = traceback.format_exc(e)
        print exstr
    mailserver.quit()
    print 'Email has been sent!'
