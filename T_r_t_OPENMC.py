import openmc
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Параметры модели
R = 0.0525  # Радиус активной зоны, м
r_fuel = 0.5  # Радиус ТВЭЛов, м
time_duration = 10  # Продолжительность моделирования, с
alpha_fuel = 10e-5  # Теплопроводность ТВЭЛов, м^2/с
alpha_moderator = 50e-6  # Теплопроводность замедляющего элемента, м^2/с
pulse_duration = 0.1  # Длительность импульса, с
tau = 0.5  # Характерное время спада тепловыделения, с
r_points = 100  # Количество точек по радиусу
t_points = 200  # Количество точек по времени

# Сетка по радиусу и времени
r = np.linspace(0, R, r_points)
t = np.linspace(0, time_duration, t_points)
# Начальные условия для температуры
T_initial = np.zeros_like(r)

# Функция для расчета плотности тепловыделения с использованием OpenMC
def calculate_heat_source(neutron_flux):
    # Создание модели OpenMC
    mat_fuel = openmc.Material()
    mat_fuel.add_element('U', 1, enrichment=5.0)
    mat_fuel.set_density('g/cm3', 10.5)

    mat_moderator = openmc.Material()
    mat_moderator.add_element('H', 2)
    mat_moderator.add_element('O', 1)
    mat_moderator.set_density('g/cm3', 1.0)

    materials = openmc.Materials([mat_fuel, mat_moderator])
    
    # Геометрия
    fuel = openmc.ZCylinder(r=r_fuel)
    fuel_cell = openmc.Cell(fill=mat_fuel, region=-fuel)
    moderator_cell = openmc.Cell(fill=mat_moderator, region=+fuel)
    
    geometry = openmc.Geometry([fuel_cell, moderator_cell])
    
    # Настройки
    settings = openmc.Settings()
    settings.batches = 50
    settings.inactive = 10
    settings.particles = 1000
    settings.run_mode = 'eigenvalue'
    
    # Источник нейтронов
    source = openmc.Source()
    source.space = openmc.stats.Point((0, 0, 0))
    source.energy = openmc.stats.Discrete([14.0e6], [1.0])
    settings.source = source
    
    # Тепловыделение
    tally = openmc.Tally()
    tally.filters = [openmc.MeshFilter(mesh)]
    tally.scores = ['heating']

    # Выполнение расчета
    model = openmc.Model(geometry, materials, settings, tallies=[tally])
    sp_file = model.run()
    
    # Обработка результатов
    with openmc.StatePoint(sp_file) as sp:
        tally = sp.get_tally(name='heating')
        heat = tally.mean.flatten()
        
    return heat

# Пример нейтронного потока (для использования в функции calculate_heat_source)
neutron_flux = 1e14  # нейтронов/см^2/с

# Тепловыделение
def Q(r, t, neutron_flux):
    heat_source = calculate_heat_source(neutron_flux)
    if r <= r_fuel:
        if t <= pulse_duration:
            return heat_source
        else:
            return heat_source * np.exp(-1 * (t - pulse_duration) / tau)
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
        Q_current = Q(r[i], t, neutron_flux)
        dTdt[i] = alpha * (T[i+1] - 2*T[i] + T[i-1]) / (r[1] - r[0])**2 + Q_current / (np.pi * r[i]**2)
    dTdt[0] = dTdt[1]  # Граничные условия на границе
    dTdt[-1] = dTdt[-2]  # Граничные условия на поверхности
    return dTdt

# Решение задачи теплопроводности
sol = solve_ivp(heat_equation, [0, time_duration], T_initial, t_eval=t, method='RK45')

# Построение графика
R, T = np.meshgrid(r/4, sol.t)
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(R, T, sol.y.T, cmap='viridis')
ax.set_xlabel('Расстояние от центра (м)')
ax.set_ylabel('Время (с)')
ax.set_zlabel('Температура (К), 293K + T*100')
plt.title('Зависимость температуры от расстояния и времени при импульсном облучении нейтронами. 0 - Комнатная температура для простоты.')
plt.savefig('T_r_t.png')
plt.show()
