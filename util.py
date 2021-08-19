import datetime
import time
from werkzeug.utils import secure_filename
import bcrypt


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


def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'),hashed_bytes_password)
