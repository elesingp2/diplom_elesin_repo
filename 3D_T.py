
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Параметры модели
R = 0.5  # Радиус активной зоны, м
r_fuel = 0.1  # Радиус ТВЭЛов, м
time_duration = 10  # Продолжительность моделирования, с
alpha_fuel = 1e-5  # Теплопроводность ТВЭЛов, м^2/с
alpha_moderator = 5e-6  # Теплопроводность замедляющего элемента, м^2/с
Q0 = 1e6  # Максимальная плотность тепловыделения во время импульса, Вт/м^3
pulse_duration = 0.1  # Длительность импульса, с
tau = 1  # Характерное время спада тепловыделения, с
r_points = 100  # Количество точек по радиусу
t_points = 200  # Количество точек по времени

# Сетка по радиусу и времени
r = np.linspace(0, R, r_points)
t = np.linspace(0, time_duration, t_points)

# Начальные условия для температуры
T_initial = np.zeros_like(r)

# Тепловыделение
def Q(r, t):
    if r <= r_fuel:
        if t <= pulse_duration:
            return Q0
        else:
            return Q0 * np.exp(-(t - pulse_duration) / tau)
    else:
        return 0

# Уравнение теплопроводности
def heat_equation(t, T):
    dTdt = np.zeros_like(T)
    for i in range(1, len(T) - 1):
        if r[i] <= r_fuel:
            alpha = alpha_fuel
        else:
            alpha = alpha_moderator
        Q_current = Q(r[i], t)
        dTdt[i] = alpha * (T[i+1] - 2*T[i] + T[i-1]) / (r[1] - r[0])**2 + Q_current / (np.pi * r[i]**2)
    dTdt[0] = dTdt[1]  # Граничные условия на границе
    dTdt[-1] = dTdt[-2]  # Граничные условия на поверхности
    return dTdt

# Решение задачи теплопроводности
sol = solve_ivp(heat_equation, [0, time_duration], T_initial, t_eval=t, method='RK45')

# Построение графика
R, T = np.meshgrid(r, sol.t)
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(R, T, sol.y.T, cmap='viridis')
ax.set_xlabel('Расстояние от центра (м)')
ax.set_ylabel('Время (с)')
ax.set_zlabel('Температура (К)')
plt.title('Зависимость температуры от расстояния и времени при импульсном облучении нейтронами')
plt.show()
