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


def highlight(phrase, message):
    return message.replace(phrase, f"<span id='highlight'>{phrase}</span>")


def delete_image(file):
    pass
