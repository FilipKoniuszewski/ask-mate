import datetime
import time
from werkzeug.utils import secure_filename


def get_milliseconds_to_date(a):
    return datetime.datetime.fromtimestamp(float(a))


def get_current_time():
    return round(time.time())


def upload_image(file):
    if file.filename != "":
        file.save("static/images/" + secure_filename(file.filename))
        image = "images/" + secure_filename(file.filename)
    else:
        image = ""
    return image


def un_inject_text(text):
    return text.replace("'", "\''")


def highligth(phrase, message):
    message = message.split(" ")
    new_message = ""
    for word in message:
        if word in phrase:
            new_message += f"<span id='highlight'>{word}</span>"
        else:
            new_message += word


def delete_image(file):
    pass

def hidding_passwords(password): ##### Działa ale zmień  !!!!
    secret = ""
    for x in range(len(password)):
        numero = ord(password[x])
        try:
            if 0 < numero >= 10 :
                numero = ord(password[x]) + 7
            elif 10 < numero <= 30 :
                numero = ord(password[x]) + 10
            elif 30 < numero <= 70 :
                numero = ord(password[x]) + 14
            elif 70 < numero <= 120 :
                numero = ord(password[x]) + 28
            else:
                numero = ord(password[x]) + 33
        except:
                numero = ord(password[x]) + 1
        secret+= str(chr(numero))
    return secret
