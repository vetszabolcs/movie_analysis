import os
import yagmail

my_mail = "witens11@gmail.com"
yag = yagmail.SMTP("witens11", os.environ.get("GPASS"), port=465)

def send_email(msg):
    yag.send(to=my_mail, subject="subtitle downloader", contents=msg)
