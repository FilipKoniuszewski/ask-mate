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
