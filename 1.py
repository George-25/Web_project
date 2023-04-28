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
openweathermap_key = "078007e7d84335abcc1c77d2160b20e3"
accuweather_key = "xVwx5iGlsnoziBNp1ZbGJJnJ1PfO1tPh"
weatherapi_key = '883b49c44e0542b6b51201949232504'
tomorrow_key = "CkmUQHdwsAvkX9VfjkxuzEXl4V8Wz8Pm"
table_name = ''
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


@app.route('/weather_forecast', methods=['GET', 'POST'])
def weather_forecast():
    name_city = f"{request.form['name_city']},RU"
    name_city2 = request.form['name_city']
    city_param = name_city2
    # ------------------------------------------------------------------------------------------------------------------
    conn = sqlite3.connect('db/blogs.db')
    cur = conn.cursor()
    city1 = cur.execute(f"""SELECT city FROM bebra
                WHERE city = ?""", (name_city2,)).fetchall()
    if len(city1) == 0 and table_name != '':
        with conn:
            cur.execute(f"""INSERT INTO {table_name}(city)
                                VAlUES(?);""", (name_city2,))
    conn.commit()
    conn.close()
    # ------------------------------------------------------------------------------------------------------------------
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather?",
                           params={'q': name_city, 'units': 'metric', 'lang': 'ru', 'APPID': openweathermap_key})
        data = res.json()
        openweather_par0 = 'Openweathermap.org'
        openweather_par1 = f"{upcase_first_letter(data['weather'][0]['description'])}"
        openweather_par2 = f"Температура: {data['main']['temp']} ℃"
        openweather_par3 = f"Ощущается как: {data['main']['feels_like']} ℃"
        openweather_par4 = f"Минимальная температура: {data['main']['temp_min']} ℃"
        openweather_par5 = f"Максимальная температура: {data['main']['temp_max']} ℃"
        openweather_par6 = f"Скорость ветра: {data['wind']['speed']} м/с"
        openweather_par7 = f"Атмосферное давление: {data['main']['pressure']} hPa"
        openweather_par8 = f"Влажность воздуха: {data['main']['humidity']} %"
        # --------------------------------------------------------------------------------------------------------------
        res_location = requests.get("http://dataservice.accuweather.com/locations/v1/cities/search?",
                                    params={'apikey': accuweather_key, 'q': name_city2, 'language': 'ru'})
        data_2 = res_location.json()
        lok_key = data_2[0]['Key']
        res_temp = requests.get(f"http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{lok_key}",
                                params={'apikey': accuweather_key, 'metric': 'true', 'details': 'true',
                                        'language': 'ru'})
        data_3 = res_temp.json()
        accuweather_par0 = 'Accuweather.com'
        accuweather_par1 = 'Сводка за полседний час:'
        accuweather_par2 = f"{upcase_first_letter(data_3[0]['IconPhrase'])}"
        accuweather_par3 = f"Температура: {data_3[0]['Temperature']['Value']} ℃"
        accuweather_par4 = f"Ощущается как: {data_3[0]['RealFeelTemperature']['Value']} ℃"
        accuweather_par5 = f"Скорость ветра: {data_3[0]['Wind']['Speed']['Value']} км/ч"
        accuweather_par6 = f"Направление ветра: {data_3[0]['Wind']['Direction']['Localized']}"
        accuweather_par7 = f"Влажность воздуха: {data_3[0]['RelativeHumidity']} %"
        accuweather_par8 = f"Вероятность выпадения осадков: {data_3[0]['PrecipitationProbability']} %"
        # --------------------------------------------------------------------------------------------------------------
        res_w = requests.get("http://api.weatherapi.com/v1/current.json?",
                             params={'key': weatherapi_key, 'lang': 'ru', 'query': name_city2})
        data_4 = res_w.json()
        weatherapi_par0 = 'Weatherapi.com'
        weatherapi_par1 = f"{upcase_first_letter(data_4['current']['condition']['text'])}"
        weatherapi_par2 = f"Температура: {data_4['current']['temp_c']} ℃"
        weatherapi_par3 = f"Ощущается как: {data_4['current']['feelslike_c']} ℃"
        weatherapi_par4 = f"Скорость ветра: {data_4['current']['wind_kph']} км/ч"
        weatherapi_par5 = f"Атмосферное давление: {str(int(data_4['current']['pressure_mb']))} hPa"
        weatherapi_par6 = f"Количество осадков: {data_4['current']['precip_mm']} мм"
        weatherapi_par7 = f"Влажность воздуха: {data_4['current']['humidity']} %"
        weatherapi_par8 = f"Облачный покров: {data_4['current']['cloud']} %"
        # --------------------------------------------------------------------------------------------------------------
        res_t = requests.get("https://api.tomorrow.io/v4/weather/realtime?",
                             params={'apikey': tomorrow_key, 'location': name_city2, 'language': 'ru',
                                     'metric': 'true'})
        data_5 = res_t.json()
        tomorrow_par0 = 'Tomorrow.io'
        tomorrow_par1 = f"Температура: {data_5['data']['values']['temperature']} ℃"
        tomorrow_par2 = f"Ощущается как: {data_5['data']['values']['temperatureApparent']} ℃"
        tomorrow_par3 = f"Облачность: {data_5['data']['values']['cloudCover']} %"
        tomorrow_par4 = f"Скорость ветра: {data_5['data']['values']['windSpeed']} м/с"
        tomorrow_par5 = f"Видимость: {data_5['data']['values']['visibility']} км"
        tomorrow_par6 = f"Влажность воздуха: {data_5['data']['values']['humidity']} %"
        tomorrow_par7 = f"Атмосферное давление: {data_5['data']['values']['pressureSurfaceLevel']} hPa"
        tomorrow_par8 = f"Вероятность выпадения осадков: {data_5['data']['values']['precipitationProbability']} %"
    except Exception:
        city_param = 'Город с таким названием не найден.'
        return render_template("index.html", city_param=city_param)
    return render_template("weather_forecast.html",
                           city_param=city_param,
                           openweather_par0=openweather_par0, openweather_par1=openweather_par1,
                           openweather_par2=openweather_par2, openweather_par3=openweather_par3,
                           openweather_par4=openweather_par4, openweather_par5=openweather_par5,
                           openweather_par6=openweather_par6, openweather_par7=openweather_par7,
                           openweather_par8=openweather_par8,
                           accuweather_par0=accuweather_par0, accuweather_par1=accuweather_par1,
                           accuweather_par2=accuweather_par2, accuweather_par3=accuweather_par3,
                           accuweather_par4=accuweather_par4, accuweather_par5=accuweather_par5,
                           accuweather_par6=accuweather_par6, accuweather_par7=accuweather_par7,
                           accuweather_par8=accuweather_par8,
                           weatherapi_par0=weatherapi_par0, weatherapi_par1=weatherapi_par1,
                           weatherapi_par2=weatherapi_par2, weatherapi_par3=weatherapi_par3,
                           weatherapi_par4=weatherapi_par4, weatherapi_par5=weatherapi_par5,
                           weatherapi_par6=weatherapi_par6, weatherapi_par7=weatherapi_par7,
                           weatherapi_par8=weatherapi_par8,
                           tomorrow_par0=tomorrow_par0, tomorrow_par1=tomorrow_par1, tomorrow_par2=tomorrow_par2,
                           tomorrow_par3=tomorrow_par3, tomorrow_par4=tomorrow_par4, tomorrow_par5=tomorrow_par5,
                           tomorrow_par6=tomorrow_par6, tomorrow_par7=tomorrow_par7, tomorrow_par8=tomorrow_par8
                           )


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
        global table_name
        table_name = user.name
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
