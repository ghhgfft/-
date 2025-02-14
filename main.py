from flask import Flask, render_template, request, redirect
import requests

import os
import json

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

YANDEX_API_KEY = os.environ.get('YANDEX_API_KEY')

from get_distances import get_path
from forms.first_method import FirstMethodForm

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

@app.route('/')
def index():
    return render_template('index.html', title="Главная")


@app.route('/about')
def about():
    cat_image = requests.get('https://api.thecatapi.com/v1/images/search').json()[0]['url']
    return render_template('about.html', title="Очень полезная информация", cat_image=cat_image)


@app.route('/first_method', methods=['GET', 'POST'])
def first_method():
    azs_list = []
    with open('data/azs.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            azs_list.append(line.strip())

    npz_list = []
    with open('data/npz.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            npz_list.append(line.strip())
    

    form = FirstMethodForm()
    form.set_azs_choices(azs_list)
    form.set_npz_choices(npz_list)
    if request.method == 'POST':
        points = []
        points.append(form.npz.data)
        points.extend(form.azs.data)
        points = '~'.join(points)
        return redirect(f'first_method_result/{points}')
    return render_template('first_method.html', title="Первый метод", form=form)


@app.route('/first_method_result/<points>', methods=['GET', 'POST'])
def first_method_result(points):
    points = points.split('~')
    result = get_path(points)

    all_points = {}
    with open('data/all_cords.json', 'r') as f:
        all_points = json.load(f)
    cords_list = []
    for point in result[0]:
        cords_list.append(all_points[point])
    cords_list_for_yandex = []
    for el in cords_list:
        cords_list_for_yandex.append(f'{el[1]},{el[0]}')
    cords_list_for_yandex = ','.join(cords_list_for_yandex)
    points_descriptions = []
    for point in result[0]:
        lon, lat = all_points[point][1], all_points[point][0]
        desc = f'{lon},{lat},pmwtl{result[0].index(point) + 1}'
        points_descriptions.append(desc)

    image = requests.get(f'https://static-maps.yandex.ru/v1?pl={cords_list_for_yandex}&pt={"~".join(points_descriptions)}&apikey={YANDEX_API_KEY}')
    with open('static/img/map_file.png', 'wb') as f:
        f.write(image.content)
    
    return render_template('first_method_result.html', title="Результаты", points=result[0], length=result[2])


@app.route('/second_method')
def second_method():
    return render_template('second_method.html', title="Второй метод")


app.run(debug=True) 