from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

class ContactForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Сообщение', validators=[DataRequired()])

def save_message(data):
    try:
        messages = []
        try:
            with open('messages.json', 'r', encoding='utf-8') as file:
                messages = json.load(file)
        except FileNotFoundError:
            pass
        
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messages.append(data)
        
        with open('messages.json', 'w', encoding='utf-8') as file:
            json.dump(messages, file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ContactForm()
    if form.validate_on_submit():
        message_data = {
            'name': form.name.data,
            'email': form.email.data,
            'message': form.message.data
        }
        if save_message(message_data):
            flash('Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.', 'success')
        else:
            flash('Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.', 'danger')
        return redirect(url_for('index'))
    return render_template('index.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 