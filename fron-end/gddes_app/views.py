import os
import sqlite3
import joblib
import mysql.connector
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

BASE_DIR = settings.BASE_DIR
DB_PATH = os.path.join(BASE_DIR, 'app.db')
MODEL_PATH = os.path.join(BASE_DIR, 'random_forest_model.joblib')

mydb = None
mycursor = None

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        port="3306",
        database='db'
    )
    mycursor = mydb.cursor()
except Exception:
    mydb = None
    mycursor = None


def sqlite_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def sqlite_query(query):
    return query.replace('%s', '?')


# Ensure users table exists in sqlite fallback
conn = sqlite_connect()
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password TEXT)")
conn.commit()
conn.close()


def executionquery(query, values):
    if mydb is not None:
        try:
            mycursor.execute(query, values)
            mydb.commit()
            return
        except Exception:
            pass
    c = sqlite_connect()
    c.execute(sqlite_query(query), values)
    c.commit()
    c.close()


def retrivequery1(query, values):
    if mydb is not None:
        try:
            mycursor.execute(query, values)
            return mycursor.fetchall()
        except Exception:
            pass
    c = sqlite_connect()
    data = c.execute(sqlite_query(query), values).fetchall()
    c.close()
    return [tuple(row) for row in data]


def retrivequery2(query):
    if mydb is not None:
        try:
            mycursor.execute(query)
            return mycursor.fetchall()
        except Exception:
            pass
    c = sqlite_connect()
    data = c.execute(sqlite_query(query)).fetchall()
    c.close()
    return [tuple(row) for row in data]


@csrf_exempt
def index(request):
    return render(request, 'index.html')


@csrf_exempt
def about(request):
    return render(request, 'about.html')


@csrf_exempt
def register(request):
    if request.method == "POST":
        email = request.POST.get('email', '')
        name = request.POST.get('name', '')
        password = request.POST.get('password', '')
        c_password = request.POST.get('c_password', '')
        if password == c_password:
            query = "SELECT UPPER(email) FROM users"
            email_data = retrivequery2(query)
            email_data_list = [i[0] for i in email_data]
            if email.upper() not in email_data_list:
                query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                values = (name, email, password)
                executionquery(query, values)
                return render(request, 'login.html', {'message': "Successfully Registered!"})
            return render(request, 'register.html', {'message': "This email ID is already exists!"})
        return render(request, 'register.html', {'message': "Conform password is not match!"})
    return render(request, 'register.html')


@csrf_exempt
def login(request):
    if request.method == "POST":
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = [i[0] for i in email_data]

        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password__data = retrivequery1(query, values)
            if password__data and password.upper() == password__data[0][0]:
                request.session['user_email'] = email
                return render(request, 'home.html')
            return render(request, 'login.html', {'message': "Invalid Password!!"})
        return render(request, 'login.html', {'message': "This email ID does not exist!"})
    return render(request, 'login.html')


@csrf_exempt
def home(request):
    return render(request, 'home.html')


@csrf_exempt
def prediction(request):
    if request.method == "POST":
        try:
            Nausea = int(request.POST['Nausea'])
            Lumber = int(request.POST['Lumber'])
            Urine = int(request.POST['Urine'])
            Micturition = int(request.POST['Micturition'])
            Urethra = int(request.POST['Urethra'])
            Itch = int(request.POST['Itch'])
            Swelling = int(request.POST['Swelling'])
            Inflammation = int(request.POST['Inflammation'])
            Nephritis = int(request.POST['Nephritis'])
            Irregular = int(request.POST['Irregular'])
            No_Periods = int(request.POST['No_Periods'])
            Excessive_Hair_Growth = int(request.POST['Excessive_Hair_Growth'])
            Buttocks = int(request.POST['Buttocks'])
            Belly_Fat = int(request.POST['Belly_Fat'])
            Hair_Loss = int(request.POST['Hair_Loss'])
            Acne = int(request.POST['Acne'])

            lee = [[Nausea, Lumber, Urine, Micturition, Urethra, Itch, Swelling, Inflammation,
                    Nephritis, Irregular, No_Periods, Excessive_Hair_Growth, Buttocks, Belly_Fat,
                    Hair_Loss, Acne]]

            model = joblib.load(MODEL_PATH)
            predictions = model.predict(lee)

            if predictions[0] == 0:
                result = 'Healthy'
            elif predictions[0] == 1:
                result = 'PCOS'
            else:
                result = 'UTI'
            return render(request, 'Prediction.html', {'result': result})
        except Exception as e:
            return render(request, 'Prediction.html', {'result': f'Error in prediction: {str(e)}'})

    return render(request, 'Prediction.html')



@csrf_exempt
def model_view(request):
    if request.method == 'POST':
        algorithms = request.POST.get("algo")
        accuracy = 0
        msg = ""
        if algorithms == "1":
            accuracy = 99
            msg = 'Accuracy  for DecisionTree Classifier is ' + str(accuracy) + '%'
        elif algorithms == "2":
            accuracy = 99
            msg = 'Accuracy  for RandomForestClassifier is ' + str(accuracy) + '%'
        elif algorithms == "3":
            accuracy = 74
            msg = 'Accuracy  for Support Vector Machine(SVM) is ' + str(accuracy) + '%'
        elif algorithms == "4":
            accuracy = 66
            msg = 'Accuracy  for KNeighborsClassifier is ' + str(accuracy) + '%'
        elif algorithms == "5":
            accuracy = 67
            msg = 'Accuracy  for GradientBoostingClassifier is ' + str(accuracy) + '%'

        return render(request, 'model.html', {'msg': msg, 'accuracy': accuracy})

    return render(request, 'model.html')
