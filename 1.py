import os
import sqlite3
import requests
from flask import Flask, render_template, redirect, request, make_response, session, jsonify
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_restful import Api

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
appid = "078007e7d84335abcc1c77d2160b20e3"
accuweather_key = "xVwx5iGlsnoziBNp1ZbGJJnJ1PfO1tPh"
api = Api(app)


def upcase_first_letter(s):
    return s[0].upper() + s[1:]


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60)
    return res


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/get-text', methods=['GET', 'POST'])
def foo():
    name_city = f"{request.form['name_city']},RU"
    # conn = sqlite3.connect('db/blogs.db')
    # with conn:
    #     conn.execute(f"""INSERT INTO {name_table}(city)
    #                         VAlUES({name_city});
    #                         """)
    # conn.commit()
    # conn.close()
    try:
        # -------------------------------------------------------------------------------------
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'q': name_city, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()
        par = 'Openweathermap.org'
        par_0 = f"{request.form['name_city']}"
        par_1 = f"{upcase_first_letter(data['weather'][0]['description'])}"
        par_2 = f"Температура: {data['main']['temp']} ℃"
        par_3 = f"Ощущается как: {data['main']['feels_like']} ℃"
        par_4 = f"Минимальная температура: {data['main']['temp_min']} ℃"
        par_5 = f"Максимальная температура: {data['main']['temp_max']} ℃"
        par_6 = f"Атмосферное давление: {data['main']['pressure']} hPa"
        par_7 = f"Влажность воздуха: {data['main']['humidity']} %"
        # --------------------------------------------------------------------------------------
        # res_location = requests.get("http://dataservice.accuweather.com/locations/v1/cities/search?",
        #                             params={'apikey': accuweather_key, 'q': name_city, 'language': 'ru'})
        # data_2 = res_location.json()
        # lok_key = data_2[0]['Key']
        # res_temp = requests.get(f"http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{lok_key}",
        #                         params={'apikey': accuweather_key, 'metric': 'true',
        #                                 'language': 'ru'})
        # data_3 = res_temp.json()
        # par0 = 'Accuweather.com'
        # par1 = 'Сводка за полседний час'
        # par2 = f"{request.form['name_city']}"
        # par3 = f"{upcase_first_letter(data_3[0]['IconPhrase'])}"
        # par4 = f"Температура: {data_3[0]['Temperature']['Value']} ℃"
        # par5 = f"Вероятность осадков: {data_3[0]['PrecipitationProbability']} %"
    except Exception as e:
        par = ''
        par_0 = ''
        par_1 = 'Город с таким названием не найден.'
        par_2 = ''
        par_3 = ''
        par_4 = ''
        par_5 = ''
        par_6 = ''
        par_7 = ''
        # par0 = ''
        # par1 = ''
        # par2 = ''
        # par3 = ''
        # par4 = ''
        # par5 = ''
    return render_template("index.html", par=par, par_0=par_0, par_1=par_1, par_2=par_2, par_3=par_3, par_4=par_4,
                           par_5=par_5, par_6=par_6,
                           # par0=par0, par1=par1, par2=par2, par3=par3, par4=par4, par5=par5,
                           par_7=par_7)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        conn = sqlite3.connect('db/blogs.db')
        with conn:
            conn.execute(f"""CREATE TABLE {form.name.data}(
                        id INT PRIMARY KEY,
                        city TEXT);
                        """)
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/blogs.db")
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
