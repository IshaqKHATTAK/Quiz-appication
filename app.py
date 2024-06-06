from flask import Flask, redirect, url_for, render_template, request, flash
import os
from werkzeug.utils import secure_filename
import sqlite3
from flask import session
from assistant import generate_quiz
from injest import Injest
from model import final_result, extract_questions
ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = './upload'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.secret_key = 'qwertyuioplkjhgfdsa'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def landing_page():
    return render_template("landing.html")


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Insert data into the database
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                     (username, email, password))
        conn.commit()
        conn.close()

        # Redirect to a success page or any other page you want
        return render_template("sucess.html")
    else:
        return render_template("signup.html")


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE name=? AND password=?", (username, password))
        user = cur.fetchone()  # Fetch one matching record
        conn.close()
        if user:
            return redirect(url_for('main'))
            # Record exists for the provided username and password
            # You can redirect the user to a success page or perform other actions
        else:
            return render_template("login.html", error="Invalid username or password")
            # Record does not exist or credentials are incorrect
            # You can redirect the user back to the login page or show an error message
    return render_template("login.html")

@app.route('/main')
def main():
    return render_template("index.html")

@app.route('/quiz_form', methods = ["get","post"])
def generate_quiz():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('Please select a file to upload')
            return redirect(request.url)
        if "file" in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                i = Injest()
                i.clear_folder()
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('attempt'))
            else:
                return f"<h1>Upload a valid formate .pdf</h1>"
    else:
        return render_template("quiz_form.html")

@app.route('/attempt')
def attempt():
    i = Injest()
    u_input = "20 questions"
    field = "Generate 20 questions with four options A, B, C, D from given document ensure the 20 questions should cover all the concept in the document."
    #creating embedings
    data = i.load_documents()
    texts = i.split_text(data)
    emb = i.get_embeddings(texts)
    i.save_embeddings(texts, emb)

    #run model to generate quiz
    response = final_result(u_input, field)
    questsions =  extract_questions(response)
    session['total_ques'] = len(questsions)
    
    if (session['total_ques']) < 6:
        return redirect(url_for('attempt'))
    return render_template("form.html",questions = questsions)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if request.method == 'POST':
        for i in range(session['total_ques']):
            question_key = f'question{i}_text'
            question_text = request.form.get(question_key)

            answer_key = f'answer{i}'
            selected_option = request.form.get(answer_key)

            # Insert data into the database
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute('INSERT INTO questions (name, question, uanswer) VALUES (?, ?, ?)',
                     (session['username'], question_text, selected_option))
            conn.commit()
            conn.close()
    # After processing, redirect to the thank you page
    return redirect(url_for('thank_you'))


@app.route('/thank_you')
def thank_you():
    return render_template('thankyou.html')

if __name__ == "__main__":
    app.run(debug=True)