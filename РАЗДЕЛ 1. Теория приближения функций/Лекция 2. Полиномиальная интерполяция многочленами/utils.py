import numpy as np

def lagrange_interpolation(x, xi, yi):
    """
    Вычисляет значение интерполяционного многочлена Лагранжа в точках x.
    
    Параметры:
        x  : массив точек, в которых нужно вычислить многочлен
        xi : массив узлов (x-координаты)
        yi : массив значений функции в узлах
    
    Возвращает:
        массив значений многочлена в точках x
    """
    x = np.asarray(x)
    n = len(xi)
    result = np.zeros_like(x, dtype=float)
    
    for i in range(n):
        li = np.ones_like(x)
        for j in range(n):
            if i != j:
                li *= (x - xi[j]) / (xi[i] - xi[j])
        result += yi[i] * li
    
    return result