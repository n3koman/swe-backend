from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from dotenv import load_dotenv
import os
import random
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Секретный ключ для сессий и сообщений
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Подключение к базе данных
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
load_dotenv()

admin = Admin(app)



class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)  # Логин пользователя
    password = db.Column(db.String(150), nullable=False)  # Пароль пользователя
    display_name = db.Column(db.String(150), unique=True, nullable=False)  # Отображаемое имя

    def check_password(self, entered):
        return check_password_hash(self.password, entered)

class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)  # Логин пользователя
    password = db.Column(db.String(150), nullable=False)  # Пароль пользователя
    display_name = db.Column(db.String(150), unique=True, nullable=False)  # Отображаемое имя

    def check_password(self, entered):
        return check_password_hash(self.password, entered)




# Команда для создания базы данных

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register_customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        display_name = request.form.get('display_name')

        # Проверка совпадения паролей
        if password != confirm_password:
            flash('Пароли не совпадают, попробуйте снова.', 'danger')
            return redirect(url_for('register_customer'))

        # Проверка уникальности логина и имени
        existing_user = Customer.query.filter((Customer.username == username) | (Customer.display_name == display_name)).first()
        if existing_user:
            flash('Логин или отображаемое имя уже используются.', 'danger')
            return redirect(url_for('register_customer'))

        # Хеширование пароля и сохранение пользователя в базе данных
        password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Customer(username=username, password=password, display_name=display_name)
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти в систему.', 'success')
        return redirect(url_for('index'))

    return render_template('register_customer.html')

@app.route('/register_farmer', methods=['GET', 'POST'])
def register_farmer():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        display_name = request.form.get('display_name')

        # Проверка совпадения паролей
        if password != confirm_password:
            flash('Пароли не совпадают, попробуйте снова.', 'danger')
            return redirect(url_for('register_farmer'))

        # Проверка уникальности логина и имени
        existing_user = Farmer.query.filter((Farmer.username == username) | (Farmer.display_name == display_name)).first()
        if existing_user:
            flash('Логин или отображаемое имя уже используются.', 'danger')
            return redirect(url_for('register_farmer'))

        # Хеширование пароля и сохранение пользователя в базе данных
        password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Farmer(username=username, password=password, display_name=display_name)
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти в систему.', 'success')
        return redirect(url_for('index'))

    return render_template('register_farmer.html')



@app.route('/login_customer', methods=['GET', 'POST'])
def login_customer():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Customer.query.filter_by(username=username).first()
        if user and user.check_password(password):
        # Если логин и пароль верны, сохраняем user_id в сессии
            session['user_id'] = user.id
            session['display_name'] = user.display_name  # Сохраняем отображаемое имя
            flash(f'Добро пожаловать, {user.display_name}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неправильный логин или пароль. Попробуйте снова.', 'danger')

    return render_template('login_customer.html')

@app.route('/login_farmer', methods=['GET', 'POST'])
def login_farmer():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Farmer.query.filter_by(username=username).first()
        if user and user.check_password(password):
        # Если логин и пароль верны, сохраняем user_id в сессии
            session['farmer_id'] = user.id
            session['display_name'] = user.display_name  # Сохраняем отображаемое имя
            flash(f'Добро пожаловать, {user.display_name}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неправильный логин или пароль. Попробуйте снова.', 'danger')

    return render_template('login_farmer.html')

@app.route('/logout')
def logout():
    # Clear the user session (log the user out)
    session.pop('user_id', None)
    session.pop('farmer_id', None)
    flash('Вы вышли из системы.', 'success')
    return redirect(url_for('index'))

admin.add_view(ModelView(Customer, db.session))
admin.add_view(ModelView(Farmer, db.session))

if __name__ == '__main__':
    app.run(debug=True)
