# app.py
from flask import Flask, render_template
from config import SECRET_KEY
from models import init_db
from api import api
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    CORS(app)
    app.register_blueprint(api)
    return app

app = create_app()

# Инициализировать таблицы при старте (если нужно)
with app.app_context():
    init_db()

# --- Page routes ---
@app.route('/')
def records_page():
    return render_template('index.html')

@app.route('/students')
def students_page():
    return render_template('students.html')

@app.route('/courses')
def courses_page():
    return render_template('courses.html')

@app.route('/add')
def add_page():
    return render_template('add_edit.html')

@app.route('/delete')
def delete_page():
    return render_template('delete.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
