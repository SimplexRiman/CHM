import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, IntSlider, FloatSlider, Dropdown

# ---------- 1. Сравнение левой / правой / центральной ----------

_FUNCS = {
    'sin(x), x0=1': (lambda x: np.sin(x), lambda x: np.cos(x), 1.0),
    'exp(x), x0=0': (lambda x: np.exp(x), lambda x: np.exp(x), 0.0),
    'exp(-x), x0=1.5': (lambda x: np.exp(-x), lambda x: -np.exp(-x), 1.5),
}


def show_fd_comparison(h=0.1, func_name='sin(x), x0=1'):
    """
    Геометрия разностных формул: касательная и три секущие + ошибки.
    """
    f, fp, x0 = _FUNCS[func_name]
    exact = fp(x0)
    left = (f(x0) - f(x0 - h)) / h
    right = (f(x0 + h) - f(x0)) / h
    central = (f(x0 + h) - f(x0 - h)) / (2 * h)

    xs = np.linspace(x0 - 4 * h, x0 + 4 * h, 400)
    plt.figure(figsize=(9, 5.5))
    plt.plot(xs, f(xs), color='#1f77b4', linewidth=2, label=f'f(x), {func_name}')
    # истинная касательная
    plt.plot(xs, f(x0) + exact * (xs - x0), 'k-', linewidth=1.5,
             label=f'касательная (точно, f\'={exact:.4f})')
    # секущие
    plt.plot([x0 - h, x0], [f(x0 - h), f(x0)], 'o--', label=f'левая: {left:.4f}')
    plt.plot([x0, x0 + h], [f(x0), f(x0 + h)], 's--', label=f'правая: {right:.4f}')
    plt.plot([x0 - h, x0 + h], [f(x0 - h), f(x0 + h)], 'd-',
             label=f'центральная: {central:.4f}')
    plt.scatter([x0], [f(x0)], s=60, c='k', zorder=5)

    info_text = (
        f"h = {h:.3f}\n"
        f"левая err: {abs(left - exact):.2e}\n"
        f"правая err: {abs(right - exact):.2e}\n"
        f"центр. err: {abs(central - exact):.2e}"
    )
    plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes,
             fontsize=10, color='#333333', verticalalignment='top',
             bbox=dict(facecolor='#f8f9fa', alpha=0.9, edgecolor='#ccc',
                       boxstyle='round,pad=0.5'))
    plt.title('Левая / правая / центральная: секущие против касательной',
              fontsize=12, pad=15)
    plt.xlabel('x', fontsize=10)
    plt.ylabel('f(x)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(loc='best', frameon=True, facecolor='white',
               edgecolor='none', fontsize=9)
    plt.show()


def run_fd_comparison_interactive():
    """
    Запуск интерактивного сравнения формул.
    """
    h_slider = FloatSlider(min=0.02, max=0.4, step=0.01, value=0.1,
                           description='шаг h:')
    func_menu = Dropdown(options=list(_FUNCS.keys()),
                         value='sin(x), x0=1', description='функция:')
    interact(show_fd_comparison, h=h_slider, func_name=func_menu)


# ---------- 2. Формулы Ньютона n = 1, 2, 3 ----------

def show_newton_orders(n_degree=2, x_eval=0.5):
    """
    Приближения f' при степенях интерполянта n = 1, 2, 3: чем выше n, тем лучше следим за f'.
    f(x) = exp(x), x0 = 0, h = 0.5.
    """
    f = lambda x: np.exp(x)
    x0, h = 0.0, 0.5
    xs = np.array([x0 + j * h for j in range(4)])
    ys = f(xs)
    d1 = ys[1] - ys[0]
    d2 = ys[2] - 2 * ys[1] + ys[0]
    d3 = ys[3] - 3 * ys[2] + 3 * ys[1] - ys[0]

    xg = np.linspace(-0.2, 1.7, 400)
    qg = (xg - x0) / h
    fp1 = np.full_like(xg, d1 / h)
    fp2 = (d1 + (2 * qg - 1) / 2 * d2) / h
    fp3 = (d1 + (2 * qg - 1) / 2 * d2 + (3 * qg ** 2 - 6 * qg + 2) / 6 * d3) / h
    curves = {1: fp1, 2: fp2, 3: fp3}

    plt.figure(figsize=(9, 5.5))
    plt.plot(xg, np.exp(xg), color='#1f77b4', linewidth=2,
             label="точная $f'=e^x$")
    styles = {1: ('--', 'n=1: линейная'), 2: ('--', 'n=2: квадратичная'),
              3: ('--', 'n=3: кубическая')}
    for n in [1, 2, 3]:
        lw = 2.5 if n == n_degree else 1.2
        alpha = 1.0 if n == n_degree else 0.45
        plt.plot(xg, curves[n], linestyle=styles[n][0], linewidth=lw,
                 alpha=alpha, label=styles[n][1])
    qe = (x_eval - x0) / h
    vals = {1: d1 / h,
            2: (d1 + (2 * qe - 1) / 2 * d2) / h,
            3: (d1 + (2 * qe - 1) / 2 * d2
                + (3 * qe ** 2 - 6 * qe + 2) / 6 * d3) / h}
    v = vals[n_degree]
    plt.scatter([x_eval], [v], s=70, c='red', zorder=5)
    plt.axvline(x_eval, color='red', linestyle=':', alpha=0.6)
    for xi in xs:
        plt.axvline(xi, color='gray', linestyle=':', alpha=0.4)
    plt.scatter(xs, np.exp(xs), s=35, zorder=5)

    info_text = (
        f"n = {n_degree}, x = {x_eval:.2f} (q = {qe:.2f})\n"
        f"приближение: {v:.4f}\n"
        f"точное: {np.exp(x_eval):.4f}\n"
        f"ошибка: {abs(v - np.exp(x_eval)):.2e}"
    )
    plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes,
             fontsize=10, color='#333333', verticalalignment='top',
             bbox=dict(facecolor='#f8f9fa', alpha=0.9, edgecolor='#ccc',
                       boxstyle='round,pad=0.5'))
    plt.title('Влияние степени интерполянта n на точность', fontsize=12,
              pad=15)
    plt.xlabel('x', fontsize=10)
    plt.ylabel("$f'_{approx}$", fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(loc='best', frameon=True, facecolor='white',
               edgecolor='none', fontsize=9)
    plt.show()


def run_newton_orders_interactive():
    """
    Запуск интерактива по степеням n.
    """
    n_slider = IntSlider(min=1, max=3, step=1, value=2, description='n:')
    x_slider = FloatSlider(min=-0.1, max=1.6, step=0.05, value=0.5,
                           description='точка x:')
    interact(show_newton_orders, n_degree=n_slider, x_eval=x_slider)


# ---------- 3. U-кривая оптимального шага ----------

def show_u_curve(delta=1e-6, M2=1.0):
    """
    Граница полной погрешности g(h) = 2*delta/h + M2*h/2 и её минимум.
    """
    h = np.logspace(-7, 0, 400)
    noise = 2 * delta / h
    approx = M2 * h / 2
    g = noise + approx
    h_opt = 2 * np.sqrt(delta / M2)
    g_min = 2 * delta / h_opt + M2 * h_opt / 2
    bits_lost = 0.5 * np.log2(1.0 / max(delta, 1e-300))

    plt.figure(figsize=(9, 5.5))
    plt.loglog(h, noise, '--', label='шум $2\\delta/h$ (растёт при $h\\to0$)')
    plt.loglog(h, approx, '--',
               label='аппроксимация $M_2h/2$ (растёт при $h\\uparrow$)')
    plt.loglog(h, g, linewidth=2, label='полная граница $g(h)$')
    plt.scatter([h_opt], [g_min], s=70, c='red', zorder=5)
    info_text = (
        f"$\\delta$ = {delta:.0e}, $M_2$ = {M2:.2f}\n"
        f"$h_opt$ = {h_opt:.2e}\n"
        f"$g_min$ = {g_min:.2e}\n"
        f"теряем ~1/2 цифр"
    )
    plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes,
             fontsize=10, color='#333333', verticalalignment='top',
             bbox=dict(facecolor='#f8f9fa', alpha=0.9, edgecolor='#ccc',
                       boxstyle='round,pad=0.5'))
    plt.title('Оптимальный шаг: слишком малый h вредит при шумных y',
              fontsize=12, pad=15)
    plt.xlabel('h', fontsize=10)
    plt.ylabel('граница ошибки', fontsize=10)
    plt.grid(True, which='both', linestyle=':', alpha=0.5)
    plt.legend(loc='best', frameon=True, facecolor='white',
               edgecolor='none', fontsize=9)
    plt.show()
    print(f"h_opt = 2*sqrt(delta/M2) = {h_opt:.3e}, "
          f"g_min = {g_min:.3e} (потеря ~половины бит при delta=2^-m)")


def run_u_curve_interactive():
    """
    Запуск интерактива U-кривой.
    """
    delta_slider = FloatSlider(min=-12, max=-3, step=1, value=-6,
                               description='log10 δ:')
    M2_slider = FloatSlider(min=0.2, max=5.0, step=0.2, value=1.0,
                            description='M2:')
    interact(lambda log10_delta, M2: show_u_curve(10 ** log10_delta, M2),
             log10_delta=delta_slider, M2=M2_slider)


# ---------- 4. Некорректность: sin(k^2 x)/k ----------

def show_illposed(k=5):
    """
    Шум sin(k^2 x)/k убывает (1/k), а его производная взрывается (k).
    """
    xs = np.linspace(0, 1, 600)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), sharex=True)
    for kk in [2, 5, 10]:
        ax1.plot(xs, np.sin(kk ** 2 * xs) / kk, linewidth=1.5,
                 alpha=0.9 if kk == k else 0.3,
                 label=f'k={kk}' + (' ←' if kk == k else ''))
        ax2.plot(xs, kk * np.cos(kk ** 2 * xs), linewidth=1.5,
                 alpha=0.9 if kk == k else 0.3,
                 label=f'k={kk}' + (' ←' if kk == k else ''))
    ax1.set_title('Шум в данных: амплитуда 1/k → 0', fontsize=11)
    ax1.set_xlabel('x')
    ax1.set_ylabel('ошибка данных')
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.legend(fontsize=9)
    ax2.set_title('Ошибка производной: амплитуда k → ∞', fontsize=11)
    ax2.set_xlabel('x')
    ax2.set_ylabel('ошибка производной')
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend(fontsize=9)
    fig.suptitle(f'Некорректность: k={k} (выделено)', fontsize=12)
    fig.tight_layout()
    plt.show()
    print(f"При k={k}: шум <= {1 / k:.3f}, а ошибка производной ~ {k} — "
          f"сколь угодно малый шум даёт сколь угодно большую ошибку.")


def run_illposed_interactive():
    """
    Запуск интерактива некорректности.
    """
    k_slider = IntSlider(min=1, max=15, step=1, value=5, description='k:')
    interact(show_illposed, k=k_slider)
