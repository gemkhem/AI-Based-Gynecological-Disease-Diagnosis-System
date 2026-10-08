import os
import sqlite3
import joblib
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

try:
    import mysql.connector
except ImportError:
    mysql = None

BASE_DIR = settings.BASE_DIR
DB_PATH = os.path.join(BASE_DIR, 'app.db')
MODEL_PATH = os.path.join(BASE_DIR, 'random_forest_model.joblib')

# In-memory cached model reference to avoid reloading 10MB pickle on every request
_MODEL_CACHE = None


def get_model():
    """Lazily load and cache the Random Forest model in memory."""
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        if os.path.exists(MODEL_PATH):
            _MODEL_CACHE = joblib.load(MODEL_PATH)
        else:
            # Fallback path if running from root without inner model duplicate
            alt_path = os.path.join(os.path.dirname(BASE_DIR), 'backend', 'random_forest_model.joblib')
            if os.path.exists(alt_path):
                _MODEL_CACHE = joblib.load(alt_path)
            else:
                raise FileNotFoundError(f"Trained Random Forest model not found at {MODEL_PATH}")
    return _MODEL_CACHE


mydb = None
mycursor = None

if mysql is not None:
    try:
        mydb = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            port=os.getenv("MYSQL_PORT", "3306"),
            database=os.getenv("MYSQL_DATABASE", "db"),
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


# Ensure users table exists in SQLite fallback
conn = sqlite_connect()
conn.execute(
    """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )"""
)
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


# ─── Application Views ────────────────────────────────────────────────────────

@csrf_exempt
def index(request):
    return render(request, 'index.html')


@csrf_exempt
def about(request):
    return render(request, 'about.html')


@csrf_exempt
def register(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        name = request.POST.get('name', '').strip()
        password = request.POST.get('password', '')
        c_password = request.POST.get('c_password', '')

        if password != c_password:
            return render(request, 'register.html', {'message': "Confirm password does not match!"})

        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = [i[0] for i in email_data]

        if email.upper() in email_data_list:
            return render(request, 'register.html', {'message': "This email address is already registered!"})

        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        values = (name, email, password)
        executionquery(query, values)
        return render(request, 'login.html', {'message': "Successfully registered! Please sign in."})

    return render(request, 'register.html')


@csrf_exempt
def login(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = [i[0] for i in email_data]

        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password_data = retrivequery1(query, values)
            if password_data and password.upper() == password_data[0][0]:
                request.session['user_email'] = email
                return render(request, 'home.html')
            return render(request, 'login.html', {'message': "Invalid password, please try again."})

        return render(request, 'login.html', {'message': "This email address does not exist."})

    return render(request, 'login.html')


@csrf_exempt
def home(request):
    return render(request, 'home.html')


@csrf_exempt
def prediction(request):
    if request.method == "POST":
        try:
            nausea = int(request.POST.get('Nausea', 0))
            lumber = int(request.POST.get('Lumber', 0))
            urine = int(request.POST.get('Urine', 0))
            micturition = int(request.POST.get('Micturition', 0))
            urethra = int(request.POST.get('Urethra', 0))
            itch = int(request.POST.get('Itch', 0))
            swelling = int(request.POST.get('Swelling', 0))
            inflammation = int(request.POST.get('Inflammation', 0))
            nephritis = int(request.POST.get('Nephritis', 0))
            irregular = int(request.POST.get('Irregular', 0))
            no_periods = int(request.POST.get('No_Periods', 0))
            excessive_hair = int(request.POST.get('Excessive_Hair_Growth', 0))
            buttocks = int(request.POST.get('Buttocks', 0))
            belly_fat = int(request.POST.get('Belly_Fat', 0))
            hair_loss = int(request.POST.get('Hair_Loss', 0))
            acne = int(request.POST.get('Acne', 0))

            feature_vector = [[
                nausea, lumber, urine, micturition, urethra, itch, swelling, inflammation,
                nephritis, irregular, no_periods, excessive_hair, buttocks, belly_fat,
                hair_loss, acne
            ]]

            model = get_model()
            predictions = model.predict(feature_vector)

            result_map = {0: 'Healthy', 1: 'PCOS', 2: 'UTI'}
            result = result_map.get(int(predictions[0]), 'Healthy')

            return render(request, 'Prediction.html', {'result': result})
        except Exception as e:
            return render(request, 'Prediction.html', {'result': f'Error in prediction: {str(e)}'})

    return render(request, 'Prediction.html')


@csrf_exempt
def model_view(request):
    if request.method == 'POST':
        algorithms = request.POST.get("algo")
        accuracy_map = {
            "1": ("DecisionTree Classifier", 99),
            "2": ("RandomForestClassifier", 99),
            "3": ("Support Vector Machine (SVM)", 74),
            "4": ("KNeighborsClassifier", 66),
            "5": ("GradientBoostingClassifier", 67),
        }

        entry = accuracy_map.get(algorithms, ("RandomForestClassifier", 99))
        name, accuracy = entry
        msg = f"Accuracy for {name} is {accuracy}%"

        return render(request, 'model.html', {'msg': msg, 'accuracy': accuracy})

    return render(request, 'model.html')
