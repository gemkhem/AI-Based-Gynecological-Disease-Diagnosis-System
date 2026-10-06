from flask import Flask,render_template, url_for, redirect, request, session
import mysql.connector,os ,re , joblib, sqlite3
import pandas as pd
import speech_recognition as sr
from googletrans import Translator
import threading
from gtts import gTTS
# Import libraries
import nltk
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    import nltk
    nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('english'))

df = pd.read_csv('gynecological_reviews.csv')




app = Flask(__name__)
app.secret_key = 'admin'

DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')

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


if mydb is None:
    conn = sqlite_connect()
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password TEXT)")
    conn.commit()
    conn.close()


def executionquery(query,values):
    if mydb is not None:
        mycursor.execute(query,values)
        mydb.commit()
        return
    conn = sqlite_connect()
    conn.execute(sqlite_query(query), values)
    conn.commit()
    conn.close()
    return

def retrivequery1(query,values):
    if mydb is not None:
        mycursor.execute(query,values)
        data = mycursor.fetchall()
        return data
    conn = sqlite_connect()
    data = conn.execute(sqlite_query(query), values).fetchall()
    conn.close()
    return [tuple(row) for row in data]

def retrivequery2(query):
    if mydb is not None:
        mycursor.execute(query)
        data = mycursor.fetchall()
        return data
    conn = sqlite_connect()
    data = conn.execute(sqlite_query(query)).fetchall()
    conn.close()
    return [tuple(row) for row in data]
###################################

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        c_password = request.form['c_password']
        if password == c_password:
            query = "SELECT UPPER(email) FROM users"
            email_data = retrivequery2(query)
            email_data_list = []
            for i in email_data:
                email_data_list.append(i[0])
            if email.upper() not in email_data_list:
                query = "INSERT INTO users (name,email, password) VALUES ( %s, %s, %s)"
                values = (name,email, password)
                executionquery(query, values)
                return render_template('login.html', message="Successfully Registered!")
            return render_template('register.html', message="This email ID is already exists!")
        return render_template('register.html', message="Conform password is not match!")
    return render_template('register.html')

@app.route('/login',methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])

        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password__data = retrivequery1(query, values)
            if password.upper() == password__data[0][0]:
                global user_email
                user_email = email

                return render_template('home.html')
            return render_template('login.html', message= "Invalid Password!!")
        return render_template('login.html', message= "This email ID does not exist!")
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/prediction', methods = ['GET',"POST"])
def prediction():
    if request.method == "POST":
        Nausea = int(request.form['Nausea'])
        Lumber = int(request.form['Lumber'])
        Urine = int(request.form['Urine'])
        Micturition = int(request.form['Micturition'])
        Urethra = int(request.form['Urethra'])
        Itch = int(request.form['Itch'])
        Swelling = int(request.form['Swelling'])
        Inflammation = request.form['Inflammation']
        Nephritis = int(request.form['Nephritis'])
        Irregular = int(request.form['Irregular'])
        No_Periods = int(request.form['No_Periods'])
        Excessive_Hair_Growth = int(request.form['Excessive_Hair_Growth'])
        Buttocks = int(request.form['Buttocks'])
        Belly_Fat = int(request.form['Belly_Fat'])
        Hair_Loss = int(request.form['Hair_Loss'])
        Acne = int(request.form['Acne'])

        lee = [[Nausea, Lumber, Urine, Micturition,Urethra, Itch, Swelling,Inflammation, Nephritis, Irregular,
                 No_Periods, Excessive_Hair_Growth, Buttocks, Belly_Fat, Hair_Loss, Acne]]
        
        print(lee)
        model = joblib.load("random_forest_model.joblib")
        
        predictions = model.predict(lee)
        print(predictions)
        if predictions == 0:
            result = 'Healthy'
            return render_template('prediction.html', result = result)
        elif predictions == 1:
            result = 'PCOS'
            return render_template('prediction.html', result = result)
        else:
            result = 'UTI'
            return render_template('prediction.html', result = result)
    return render_template('prediction.html')

@app.route('/voice', methods = ["GET", "POST"])
def voice():
    my_text = None
    translated_text = None
    if request.method == "POST":
        language = request.form["language"]

        # Dictionary of Indian languages
        indian_languages = {
            'hi': 'Hindi',
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'gu': 'Gujarati',
            'mr': 'Marathi',
            'or': 'Odia',
            'pa': 'Punjabi',
            'as': 'Assamese',
            'sd': 'Sindhi',
            'ur': 'Urdu',
            'ne': 'Nepali'
        }

        # Print available languages for the user to choose
        print("Available Indian languages:")
        for code, lang in indian_languages.items():
            print(f"{code}: {lang}")

        # Get user input for the language code
        language_code = language.strip()

        # Validate user input
        if language_code not in indian_languages:
            print("Invalid language code.")
            exit()

        # Create a speech recognition object
        r = sr.Recognizer()

        # Use the microphone as the audio source
        with sr.Microphone() as source:
            print(f"Please say something in {indian_languages[language_code]}:")
            audio = r.listen(source)

        # Save the audio file
        with open("input.wav", "wb") as f:
            f.write(audio.get_wav_data())

        # Recognize the speech
        try:
            my_text = r.recognize_google(audio, language=f"{language_code}-IN")
            print("You said: " + my_text)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            exit()

        # Translate the text to English
        translator = Translator()
        translated_text = translator.translate(my_text, dest="en").text
        print("Translated text To English : " + translated_text)

        # Convert the translated text to speech
        # output = gTTS(text=translated_text, lang="en", slow=True)
        # output.save("static/saves_audio/output.mp3")
        # os.system("start output.mp3")
        



        # For Reviews Comparision

        def preprocess_text(text):## ["revn ["rnbnnfn"]p"]
            """
            Preprocesses the input text by removing non-alphabetic characters,
            converting to lowercase, tokenizing, stemming, and removing stopwords.
            
            Parameters:
            text (str): The input text to preprocess.
            
            Returns:
            str: The processed text.
            """
            ps = PorterStemmer()
            stop_words = set(stopwords.words('english'))
            
            # Remove non-alphabetic characters
            text = re.sub('[^a-zA-Z]', ' ', text)
            
            # Convert to lowercase
            text = text.lower()
            
            # Tokenize the text
            words = word_tokenize(text)
            
            # Remove stopwords and apply stemming
            processed_words = [ps.stem(word) for word in words if word not in stop_words]
            
            # Join the processed words back into a string
            processed_text = ' '.join(processed_words)
            
            return processed_text

        def find_most_similar_review(input_text, df):
            """
            Finds the review most similar to the input text based on cosine similarity.
            
            Parameters:
            input_text (str): The input text to compare with the reviews.
            df (pd.DataFrame): DataFrame containing a 'clean_review' column with reviews.
            
            Returns:
            str: The most similar review from the dataframe.
            """
            # Preprocess the input text
            input_text_processed = preprocess_text(input_text)
            
            # Preprocess the reviews in the dataframe
            df['processed_review'] = df['Review'].apply(preprocess_text)
            
            # Create a list of processed reviews
            reviews = df['processed_review'].tolist()
            
            # Append the input text to the list of reviews
            reviews.append(input_text_processed)
            
            # Compute TF-IDF vectors
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(reviews)
            
            # Compute cosine similarity
            cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
            
            # Get the index of the most similar review
            most_similar_index = cosine_sim.argmax()
            
            # Return the most similar review
            return df['Review'].iloc[most_similar_index]


        input_text = translated_text
        # Find the most similar review
        most_similar_review = find_most_similar_review(input_text, df)
        print(f"Most similar review: {most_similar_review}")


        # Translate the text to user language
        translator2 = Translator()
        translated_text2 = translator2.translate(most_similar_review, dest=language_code).text
        print("Translated text to user lang: " + translated_text2)

        # Convert the translated text to speech
        output2 = gTTS(text=translated_text2, lang=language_code, slow=True)
        output2.save("static/saves_audio/output.mp3")
        # os.system("start output.mp3")



        return render_template('voice.html', my_text = my_text, translated_text = translated_text, most_similar_review = most_similar_review)
    return render_template('voice.html')




@app.route('/model',methods =['GET','POST'])
def model():

    if request.method == 'POST':
        algorithams = request.form["algo"]
        if algorithams == "1":
            accuracy = 99
            msg = 'Accuracy  for DecisionTree Classifier is ' + str(accuracy) + str('%')
        elif algorithams == "2":
            accuracy = 99
            msg = 'Accuracy  for RandomForestClassifier is ' + str(accuracy) + str('%')
        elif algorithams == "3":
            accuracy = 74
            msg = 'Accuracy  for Support Vector Machine(SVM) is ' + str(accuracy) + str('%')
        elif algorithams == "4":
            accuracy = 66
            msg = 'Accuracy  for KNeighborsClassifier is ' + str(accuracy) + str('%')
        elif algorithams == "5":
            accuracy = 67
            msg = 'Accuracy  for GradientBoostingClassifier is ' + str(accuracy) + str('%')
        return render_template('model.html',msg=msg,accuracy = accuracy)
    return render_template('model.html')



    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)