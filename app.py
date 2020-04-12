'''
session dictionary holds 

session = {
    'user_id': key,
    'user_national_id': key,
    'username': key
    'results' : []
}
'''
import os
from helpers import login_required, apology, convert_date_to_dict
from datetime import datetime, date
from pytz import timezone
from tempfile import mkdtemp
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import pyqrcode
import png

# configure the flask app
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure the database.
# export DATABASE_URL="postgresql:///covid-19" or the URL of the database hosted on heroku
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# declare the insertion date
today = str(date.today())
print(type(today))



# declare a function to query the database questions table
@app.route("/questions/load_questions/<string:questionno>")
@login_required
def load_questions(questionno):

    if int(questionno) > 9:
        return "over"

    rows = db.execute("SELECT * FROM questions WHERE id = :var1", {"var1": questionno}).fetchone()

    # print(rows.question)
    if not rows:
        return "over"
    
    else:
        return render_template("questions.html", data = rows)


@app.route("/questions/load_total_que")
@login_required
def load_total_que():

    rows = db.execute('SELECT * FROM questions').fetchall()
    if not rows:
        return apology("something went wrong :(")

    total_que = len(rows)
    print(f"hello motherfucker {total_que}")

    return str(total_que)


@app.route("/")
@login_required
def index():
    ''' query the data base for the patient data to display above the qr code. '''

    row = db.execute("SELECT * FROM users WHERE id = :var1 AND national_id = :var2",
                    {"var1": session['user_id'], "var2": session['user_national_id']}).fetchone()
    
    if not row:
        return apology("تاكد من ادخالك الرقم القومي بصورة صحيحة")

    # query the database the questions table to display the examination details in the qr code.
    answer_details = db.execute("SELECT question FROM questions").fetchall()

    if not answer_details:
        return apology("something went wrong,, report us :(")

    # retrieve the last session results from scores table and embed it to the QRcode.
    last_results = db.execute(''' SELECT * FROM scores WHERE user_id = :var1 ORDER BY id DESC''', 
                            {'var1': session['user_id']}).fetchone()

    if not last_results:
        print("data base failure dude ")

    # put the questions and the user's score for each question from the session['results']
    QRdata = f'''\n
        Last examination took place on {last_results.date}
       \n
       \n Q1 ==> {last_results.q1} \n
       \n Q2 ==> {last_results.q2} \n
       \n Q3 ==> {last_results.q3} \n
       \n Q4 ==> {last_results.q4} \n
       \n Q5 ==> {last_results.q5} \n
       \n Q6 ==> {last_results.q6} \n
       \n Q7 ==> {last_results.q7} \n
       \n Q8 ==> {last_results.q8} \n
       \n Q9 ==> {last_results.q9} \n
       \n
    '''

    code = pyqrcode.create(QRdata)
    image_as_str = code.png_as_base64_str(scale=2)

    return render_template("index.html", row=row, answer_details=answer_details, image_as_str=image_as_str)


@app.route("/before_index", methods=["GET"])
@login_required
def before_index():

    # accmulate the session['results'] to get the total score and insert it to DB.
    score = 0
    for i in session['results']:
        score += i

    print(f"here is the total score today {score}")

    db.execute('''INSERT INTO scores(user_id, result, date, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9) 
                VALUES(:var1, :var2, :var3, :q1, :q2, :q3, :q4, :q5, :q6, :q7, :q8, :q9)''',
                {
                    "var1": session["user_id"], "var2": score, "var3": today, 
                    'q1': session['results'][0],
                    'q2': session['results'][1],
                    'q3': session['results'][2],
                    'q4': session['results'][3],
                    'q5': session['results'][4],
                    'q6': session['results'][5],
                    'q7': session['results'][6],
                    'q8': session['results'][7],
                    'q9': session['results'][8]
                })

    print("data has been inserted successfully from /before_index")
    db.commit()

    return redirect(url_for("index"))


@app.route("/self-test/<string:radiovalue>/<string:questionno>", methods=['POST'])
@login_required
def self_test_two(radiovalue, questionno):
    print(radiovalue)
    print(questionno)

    # append the radio values to the session
    session['results'].append(int(radiovalue))
    print(session['results'])

    return print(f"{questionno} done")


@app.route("/self-test", methods=['GET'])
@login_required
def self_test():

    ''' access the questions answers '''
    session['results'] = []

    # query the database for score in the last 5 days to hinder the user in case of doing that twice in the same week.
    row = db.execute("SELECT date FROM scores WHERE user_id = :var1 ORDER BY id DESC",
                    {"var1": session["user_id"]}).fetchone()
    
    if not row:

        # that one means that it the first time for this user.
        return render_template('test.html')
    print(row.date)

    # pass the date of today and the date retrieved from the database to convert it to dictionary.
    today_date = convert_date_to_dict(str(today))
    last_date = convert_date_to_dict(str(row.date))

    print(today_date)
    print(last_date)
    # make the check of the last examin.
    if (today_date['day'] - last_date['day']) >= 5:

        return render_template('test.html')

    else:
        return redirect('/')


@app.route("/login", methods=['GET', 'POST'])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("الاسم غير صحيح")

        # Ensure password was submitted
        elif not request.form.get("ID"):
            return apology("خطافي الرقم القومي")

        # check the length of the national id.
        if not len(request.form.get("ID")) == 14:
            return apology("الرقم القومي غير صحيح")

        # declare the session dictionary to help in the database quering.
        # update the session to username.
        session['username'] = request.form.get("username")

        # strip the trinary name of the user out of white spaces.
        name_list = []
        total_name = request.form.get("username").strip()

        for i in total_name.split(' '):
            if i == '':
                pass
            else:
                name_list.append(i)
        
        print(name_list)

        # validate that the user entered the trinary name.
        if not len(name_list) == 3:
            return apology("لم تقم بإدخال الاسم ثلاثيا")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE first_name = :var1 AND second_name = :var2 AND last_name = :var3 AND national_id = :var4",
                {
                    'var1': name_list[0],
                    'var2': name_list[1],
                    'var3': name_list[2],
                    'var4': request.form.get("ID")
                }
            ).fetchone()
        
        # ensure the data provided from the user is exist in the database.
        if rows is None:
            return apology("هذا الا سم غير مسجل من قبل او خطا في الرقم القومي")

        # Remember which user has logged in
        session["user_id"] = rows.id
        print(session['user_id'])
        session['user_national_id'] = rows.national_id
        print(session['user_national_id'])

        # Redirect user to home page
        return redirect("/self-test")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    ''' register to the database '''
    if request.method == "POST":
        
        # access the users' data to validate
        username = request.form.get("username")
        address = request.form.get("address")
        age = request.form.get("age")
        phone = request.form.get("phone")
        ID = request.form.get("ID")

        # validate for each filed in the submition form.
        if not username or not address or not age or not phone or not ID:
            return apology("يجب ادخال كل البيانات السابقة")

        # check the length of the phone and national id
        if not len(phone) == 11:
            return apology("رقم المحمول غير صحيح")
        
        if not len(ID) == 14:
            return apology("الرقم القومي غير صحيح")

        # strip the trinary name of the user out of white spaces.
        name_list = []
        total_name = username.strip()

        for i in total_name.split(' '):
            if i == '':
                pass
            else:
                name_list.append(i)
        
        print(name_list)

        # validate that the user entered the trinary name.
        if not len(name_list) == 3:
            return apology("لم تقم بإدخال الاسم ثلاثيا")

        # insert these data into the database.
        db.execute('''INSERT INTO users(first_name, second_name, last_name, address, phone_num, national_id, age) 
                    VALUES(:var1, :var2, :var3, :var4, :var5, :var6, :var7)''',
                    {
                        "var1": name_list[0],
                        "var2": name_list[1],
                        "var3": name_list[2],
                        "var4": address, "var5": phone,
                        "var6": ID,
                        "var7": age
                    }
                )
        print("DATA HAS BEEN INSERTED SUCCESSFULLY")
        db.commit()

        # redirect to the index page.
        return redirect(url_for("self_test"))

    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    
    # loging out is just by clearing the session dictonary.
    # to forget any user in right now.
    session.clear()

    # redirect to the login page
    return redirect(url_for("index"))


@app.route("/precautions")
def precautions():

    return render_template("precautions.html")

@app.route("/quarantine")
def quarantine():

    return render_template("quarantine.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
