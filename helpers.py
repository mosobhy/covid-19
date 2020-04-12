from flask import redirect, session, render_template
from functools import wraps

def apology(message):

    return render_template("apology.html", message=message)

''' the following function takes an date in the string format and return it as a dictionary '''
def convert_date_to_dict(date):

    # declare an empty dictionary.
    dictionary_for_host = {}

    # declare the date componants
    list_for_date = ['year', 'month', 'day']

    index = 0
    for i in date.split('-'):
        dictionary_for_host[list_for_date[index]] = int(i)
        index += 1

    return dictionary_for_host


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



