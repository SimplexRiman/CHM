import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, IntSlider

def show_method_error(n_rectangles=4):
    """
    Визуализация погрешности метода прямоугольников с динамическим подсчетом ошибки.
    """
    # Исходная функция и границы
    f = lambda x: x**2
    a, b = 0, 2
    
    # Точное значение интеграла для f(x) = x^2 равно 8/3
    exact_area = 8 / 3
    
    # Сетка для отрисовки плавной кривой
    x_fine = np.linspace(a, b, 300)
    y_fine = f(x_fine)
    
    # Расчет шага и координат прямоугольников (левые прямоугольники)
    h = (b - a) / n_rectangles
    x_rect = np.linspace(a, b, n_rectangles, endpoint=False)
    y_rect = f(x_rect)
    
    # Приближенная площадь методом прямоугольников
    approx_area = np.sum(y_rect * h)
    
    # Текущая абсолютная погрешность метода
    method_error = abs(exact_area - approx_area)
    
    # Строим график с измененными пропорциями (сделали выше)
    plt.figure(figsize=(9, 7))
    plt.plot(x_fine, y_fine, color='#1f77b4', linewidth=2, label='Точная функция $f(x) = x^2$')
    plt.fill_between(x_fine, y_fine, color='#1f77b4', alpha=0.1, label=f'Точная площадь = {exact_area:.5f}')
    
    # Отрисовка столбцов в более спокойной цветовой гамме
    plt.bar(x_rect, y_rect, width=h, align='edge', 
            facecolor='none', edgecolor='#7f7f7f', hatch='//', linewidth=1,
            label=f'Приближенная площадь = {approx_area:.5f}')
    
    # Аккуратный информационный блок без страшных шрифтов и ярких цветов
    info_text = (
        f"Параметры расчета:\n"
        f"• Шагов разбиения (N): {n_rectangles}\n"
        f"• Шаг сетки (h): {h:.4f}\n"
        f"• Погрешность метода: {method_error:.5f}"
    )
    plt.text(0.05, 3.4, info_text, fontsize=10, color='#333333', 
             fontfamily='sans-serif',
             bbox=dict(facecolor='#f8f9fa', alpha=0.9, edgecolor='#ccc', boxstyle='round,pad=0.5'))
    
    plt.title('Динамическая демонстрация погрешности метода', fontsize=12, pad=15)
    plt.xlabel('X', fontsize=10)
    plt.ylabel('Y', fontsize=10)
    plt.xlim(a - 0.1, b + 0.1)
    plt.ylim(-0.2, 4.5)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='none', fontsize=9)
    plt.show()

def run_show_method_error_interactive_plot():
    """
    Запуск интерактивного ползунка.
    """
    slider = IntSlider(min=2, max=50, step=1, value=4, description='Шаги (N):')
    interact(show_method_error, n_rectangles=slider)