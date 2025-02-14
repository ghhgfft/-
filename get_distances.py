import requests

import time
import json
import random
import os
import sys
import itertools
import math

API_KEY = str(os.getenv('API_KEY'))
url = f'https://routing.api.2gis.com/carrouting/6.0.0/global?key={API_KEY}'

def get_from_distances_cache(start_point, finish_point):
    start_point_str = f'{start_point[0]}-{start_point[1]}'
    finish_point_str = f'{finish_point[0]}-{finish_point[1]}'

    all_distances = {}
    with open('data/all_distances.json') as f:
        all_distances = json.load(f)
    
    if start_point_str in all_distances.keys():
        if finish_point_str in all_distances[start_point_str].keys():
            return all_distances[start_point_str][finish_point_str]
    return None
    



def write_to_cache(start_point, finish_point, distance) -> None:
    all_distances = {}

    start_point_str = f'{start_point[0]}-{start_point[1]}'
    finish_point_str = f'{finish_point[0]}-{finish_point[1]}'

    with open('data/all_distances.json') as f:
        all_distances = json.load(f)

    if start_point_str in all_distances.keys():
        all_distances[start_point_str][finish_point_str] = distance
    else:
        all_distances[start_point_str] = {finish_point_str: distance}
    with open('data/all_distances.json', 'w') as f:
        json.dump(all_distances, f)


def get_cords(point):
    
    all_cords = {}
    with open('data/all_cords.json', encoding='utf-8') as f:
        all_cords = json.load(f)
    if point in all_cords.keys():
        return all_cords[point][0], all_cords[point][1]
    else:
        response = requests.get(f'https://catalog.api.2gis.com/3.0/items/geocode?q={point}&fields=items.point&key={API_KEY}')
        if response.status_code == 200:
            cords = response.json()['result']['items'][0]['point']
            all_cords[point] = cords['lat'], cords['lon']
            with open('data/all_cords.json', 'w', encoding='utf-8') as f:
                json.dump(all_cords, f)
            return cords['lat'], cords['lon']
        else:
            print('Неизвестная ошибка, обратитесь в поддержку(получение координат)')
            sys.exit()


def get_distance(start_point, finish_point):
    distance = get_from_distances_cache(start_point, finish_point)
    if not distance:
        data = {
        "points": [
            {
                "type": "walking",
                "lat": start_point[0],
                "lon": start_point[1]
            },
            {
                "type": "walking",
                "lat": finish_point[0],
                "lon": finish_point[1]
            }
        ],
        "type": "shortest"
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            distance = response.json()['result'][0]['total_distance']
            write_to_cache(start_point, finish_point, distance)
            return response.json()['result'][0]['total_distance']
        else:
            print('Неизвестная ошибка, обратитесь в поддержку(определение расстояния)')
    return distance


def get_distance_matrix(points):
    points_cords = []
    points_ids = {}
    for point in points:
        point_cords = get_cords(point.strip('\n'))
        if point_cords not in points_cords:
            points_cords.append(point_cords)
        if point.strip('\n') not in points_ids.values():
            points_ids[points.index(point)] = point.strip('\n')
            

    distance_matrix = []
    for start_cords in points_cords:
        row = []
        for cords in points_cords:
            if cords == start_cords:
                row.append(0)
            else:
                row.append(get_distance(start_cords, cords))
        distance_matrix.append(row)
    return distance_matrix, points_ids


def tsp_dynamic_programming(dist_matrix, points_ids):

    n = len(dist_matrix)

   

    # Инициализация dp таблицы и пути

    dp = [[float('inf')] * n for _ in range(1 << n)]

    parent = [[-1] * n for _ in range(1 << n)]  # Родитель для восстановления пути

    dp[1][0] = 0  # Начинаем с первой вершины (0)


    # Заполнение dp таблицы

    for mask in range(1, 1 << n):

        for u in range(n):

            if mask & (1 << u):

                for v in range(n):

                    if mask & (1 << v) and u != v:

                        if dp[mask][u] > dp[mask ^ (1 << u)][v] + dist_matrix[v][u]:

                            dp[mask][u] = dp[mask ^ (1 << u)][v] + dist_matrix[v][u]

                            parent[mask][u] = v


    # Находим минимальное расстояние для возвращения в начальную точку

    min_dist = float('inf')

    end_mask = (1 << n) - 1

    last_vertex = -1

    for u in range(1, n):

        if min_dist > dp[end_mask][u] + dist_matrix[u][0]:

            min_dist = dp[end_mask][u] + dist_matrix[u][0]

            last_vertex = u


    # Восстанавливаем путь

    path = []

    mask = end_mask

    while last_vertex != -1:

        path.append(last_vertex)

        next_vertex = parent[mask][last_vertex]

        mask ^= (1 << last_vertex)

        last_vertex = next_vertex

    path.reverse()

    path.append(0)  # Добавляем начальную точку


    # Преобразуем путь в имена вершин

    path_names = [points_ids[i] for i in path]
    path_ids = [i for i in path]


    return path_names, path_ids, min_dist


def floyd_checking(matrix):
    A = [[matrix[i][j] for j in range(len(matrix))] for i in range(len(matrix))] 
    Prev = [[None for j in range(len(matrix))] for i in range(len(matrix))] 
    for k in range(len(matrix)):
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if A[i][k] != 0 and A[k][j] != 0 and A[i][k] + A[k][j] < A[i][j]:
                    A[i][j] = A[i][k] + A[k][j]
                    Prev[i][j] = Prev[k][j]
    return matrix == A


def calculate_summary_distance(path, matrix):
    dist = 0
    for i in range(len(path) - 1):
        dist += matrix[path[i]][path[i + 1]]
    dist += matrix[path[-1]][path[0]]  # return to the starting point
    return dist


def anneal(matrix, points):
    state = points
    temp = 1
    n = 1e6
    i = 0
    while i < n:
        temp *= 0.99
        i+=1
        x = random.randint(1, len(state) - 2)
        y = random.randint(1, len(state) - 2)
        while x == y:
            y = random.randint(1, len(state) - 2)
        new_state = state.copy()
        new_state[x], new_state[y] = new_state[y], new_state[x]
        f_old = calculate_summary_distance(state, matrix)
        f_new = calculate_summary_distance(new_state, matrix)
        if f_old == f_new:
            continue
        if f_old > f_new:
            state = new_state
            continue
        if (random.uniform(0, 1) < math.exp((f_old - f_new) / temp)):
            state = new_state
            continue
    return state

def anneal_checking(matrix, path, path_length):
    min_path = 100000000000000000000
    annealed_path = []
    for i in range(10):
        print(f'Annealing {i+1}')
        annealed_path = anneal(matrix, path)
        ln = calculate_summary_distance(annealed_path, matrix)
        if ln < min_path:
            min_path = ln
    return min_path == path_length, path == annealed_path


def get_path(points):
    matrix, points_ids = get_distance_matrix(points)
    min_path, min_path_ids, min_distance = tsp_dynamic_programming(matrix, points_ids)

    with open('matrix.txt', 'w', encoding='utf-8') as f:
        for row in matrix:
            f.write(f'{' - '.join([str(n) for n in row])}\n')

    return min_path, min_path_ids, min_distance