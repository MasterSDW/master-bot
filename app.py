from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email
from flask_cors import CORS
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Добавляем поддержку CORS
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Ограничиваем размер запроса до 16MB

class ContactForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(message="Ім'я обов'язкове")])
    email = StringField('Email', validators=[DataRequired(message="Email обов'язковий"), Email(message="Невірний формат email")])
    message = TextAreaField('Сообщение', validators=[DataRequired(message="Повідомлення обов'язкове")])

def save_message(data):
    try:
        # Создаем директорию для файла, если она не существует
        os.makedirs('data', exist_ok=True)
        filename = 'data/messages.json'
        
        messages = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                messages = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            messages = []
        
        if not isinstance(messages, list):
            messages = []
        
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messages.append(data)
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(messages, file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ContactForm()
    if request.method == 'POST':
        try:
            # Проверяем, является ли запрос AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                if form.validate():
                    message_data = {
                        'name': form.name.data,
                        'email': form.email.data,
                        'message': form.message.data
                    }
                    if save_message(message_data):
                        return jsonify({
                            'status': 'success',
                            'message': 'Дякуємо за ваше повідомлення! Ми зв\'яжемося з вами найближчим часом.'
                        })
                    else:
                        return jsonify({
                            'status': 'error',
                            'message': 'Виникла помилка при збереженні повідомлення. Будь ласка, спробуйте пізніше.'
                        }), 500
                else:
                    errors = {field.name: field.errors[0] for field in form if field.errors}
                    return jsonify({
                        'status': 'validation_error',
                        'errors': errors
                    }), 400
            else:
                # Обычная отправка формы
                if form.validate_on_submit():
                    message_data = {
                        'name': form.name.data,
                        'email': form.email.data,
                        'message': form.message.data
                    }
                    if save_message(message_data):
                        flash('Дякуємо за ваше повідомлення! Ми зв\'яжемося з вами найближчим часом.', 'success')
                    else:
                        flash('Виникла помилка при збереженні повідомлення. Будь ласка, спробуйте пізніше.', 'danger')
                    return redirect(url_for('index'))
                else:
                    for field, errors in form.errors.items():
                        for error in errors:
                            flash(f'{error}', 'danger')
        except Exception as e:
            print(f"Error processing form: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'error',
                    'message': 'Виникла помилка при обробці форми. Будь ласка, спробуйте пізніше.'
                }), 500
            else:
                flash('Виникла помилка при обробці форми. Будь ласка, спробуйте пізніше.', 'danger')
                
    return render_template('index.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(413)
def request_entity_too_large(error):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'error',
            'message': 'Розмір даних перевищує допустимий ліміт.'
        }), 413
    else:
        flash('Розмір даних перевищує допустимий ліміт.', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 