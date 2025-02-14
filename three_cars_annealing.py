import random
import math
 
# Матрица расстояний
distances = [
    [0, 1072, 1555, 3327, 10214, 10042, 6764, 3913, 9152, 4489, 18140, 8614, 7967],
    [6660, 0, 6711, 7979, 11776, 14694, 8296, 2910, 8149, 6021, 17137, 7611, 9499],
    [1282, 1219, 0, 3474, 10361, 10189, 6911, 4060, 9299, 4636, 18287, 8761, 8114],
    [3405, 3044, 2157, 0, 7044, 7094, 4767, 5872, 10272, 3656, 18133, 10540, 6398],
    [9961, 9600, 8713, 7160, 0, 11692, 4824, 8388, 6343, 5743, 14204, 6755, 3123],
    [6847, 6486, 5599, 4046, 9864, 0, 7587, 9121, 13092, 6476, 20953, 13504, 9218],
    [5292, 4931, 4044, 2491, 9378, 7023, 0, 7759, 12606, 5990, 20467, 12427, 8732],
    [4096, 3724, 3801, 5069, 8866, 11784, 5386, 0, 5613, 3111, 14601, 5075, 6589],
    [7426, 7054, 7477, 8696, 7998, 15199, 8331, 3676, 0, 6056, 11678, 2152, 9407],
    [4444, 4083, 3196, 3619, 5907, 9295, 2427, 2797, 7745, 0, 15606, 7213, 3630],
    [11811, 11439, 11862, 11771, 7947, 16303, 9435, 8061, 4768, 10354, 0, 5427, 9356],
    [9936, 9564, 9987, 9702, 5878, 14234, 7366, 6186, 2893, 8285, 9630, 0, 7287],
    [8014, 7653, 6766, 7189, 8575, 11963, 5095, 6367, 4355, 3722, 12216, 4767, 0]
]
 
def calculate_distance(path, distances):
    distance = 0
    for i in range(len(path) - 1):
        distance += distances[path[i]][path[i + 1]]
    # Добавляем расстояние от последнего узла до начального
    distance += distances[path[-1]][path[0]]
    return distance
 
def anneal(distances, path):
    temp = 1.0
    min_temp = 1e-8
    alpha = 0.995
    max_iterations = 100000
 
    current_distance = calculate_distance(path, distances)
    best_path = path[:]
    best_distance = current_distance
 
    for i in range(max_iterations):
        if temp < min_temp:
            break
 
        # Генерация нового состояния
        new_path = path[:]
        a, b = random.sample(range(1, len(new_path) - 1), 2)
        new_path[a], new_path[b] = new_path[b], new_path[a]
 
        new_distance = calculate_distance(new_path, distances)
 
        # Принимаем новое состояние с определенной вероятностью
        if new_distance < current_distance or random.uniform(0, 1) < math.exp((current_distance - new_distance) / temp):
            path = new_path
            current_distance = new_distance
 
            # Обновляем лучшее решение
            if new_distance < best_distance:
                best_path = new_path[:]
                best_distance = new_distance
 
        temp *= alpha
 
    return best_path, best_distance
 
def solve_mtsp(distances, num_vehicles):
    n = len(distances)
    points = list(range(1, n))  # Исключаем начальную точку (0)
    random.shuffle(points)
 
    # Разделяем точки между транспортными средствами
    sub_paths = [[] for _ in range(num_vehicles)]
    for i, point in enumerate(points):
        sub_paths[i % num_vehicles].append(point)
 
    # Включаем начальную и конечную точки в каждый подмаршрут
    for sub_path in sub_paths:
        sub_path.insert(0, 0)
        sub_path.append(0)
 
    best_paths = []
    total_distance = 0
 
    # Оптимизируем каждый подмаршрут отдельно
    for sub_path in sub_paths:
        best_path, best_distance = anneal(distances, sub_path)
        best_paths.append(best_path)
        total_distance += best_distance
 
    return best_paths, total_distance
 
# Указываем количество транспортных средств
num_vehicles = 3
 
# Инициализируем лучшее решение
best_paths, best_total_distance = solve_mtsp(distances, num_vehicles)
print("Начальное решение:")
for i, path in enumerate(best_paths):
    print(f"Транспортное средство {i+1}: {path}")
print("Общее минимальное расстояние:", best_total_distance)
 
while True:
    new_paths, new_total_distance = solve_mtsp(distances, num_vehicles)
    if new_total_distance < best_total_distance:
        best_paths = new_paths
        best_total_distance = new_total_distance
        print("\nНайдено лучшее решение:")
        for i, path in enumerate(best_paths):
            print(f"Транспортное средство {i+1}: {path}")
        print("Общее минимальное расстояние:", best_total_distance)