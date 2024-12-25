from flask import Flask, request, render_template
import re
import google.generativeai as genai
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

genai.configure(api_key="{API_KEY}")
model = genai.GenerativeModel("gemini-1.5-flash")

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    choices = db.Column(db.String(1000), nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

def generate_gemini_content(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Hata: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_question():
    text = request.form['text'].strip()
    if not text:
        return render_template('index.html', question="Lütfen bir metin girin.")
    
    question = generate_gemini_content(f"{text}\nSoru: Bu metne dayalı bir soru üretir misiniz?")
    choices = generate_gemini_content(f"Soru: {question}\nBu soruya uygun 4 ayrı şık üretir misiniz? Şıkları 'A)', 'B)', 'C)', 'D)' olarak formatlayın.").split("\n")
    correct_answer = generate_gemini_content(f"Soru: {question}\nŞıklar: {', '.join(choices)}\nDoğru cevabı açıklayarak söyler misiniz?")
    
    new_question = Question(
        text=text,
        question=question,
        choices=str(choices),
        correct_answer=correct_answer
    )
    db.session.add(new_question)
    db.session.commit()

    return render_template(
        'index.html',
        question=f"Oluşturulan Soru: {question}",
        choices=choices,
        correct_answer=f"Doğru Cevap: {correct_answer}"
    )

if __name__ == '__main__':
    app.run(debug=True)
