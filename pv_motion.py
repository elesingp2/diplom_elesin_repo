import numpy as np 
from scipy.integrate import solve_ivp 
import matplotlib.pyplot as plt 
 
# Параметры системы 
P0 = 100000  # начальное давление в Паскалях 
V0 = 0.1  # начальный объем в м^3 
A = 0.01  # площадь поршня в м^2 
m = 10  # масса поршня в кг 
gamma = 1.4  # показатель адиабаты для идеального газа 
 
# Уравнение движения, переписанное для использования в solve_ivp 
def motion(t, y): 
    x, v = y  # y[0] - положение (x), y[1] - скорость (v) 
    dxdt = v  # производная положения по времени равна скорости 
    dVdt = A * dxdt  # изменение объема со временем 
    P = P0 * (V0 / (V0 + A * x))**gamma  # давление в зависимости от объема 
    dvdt = (P * A - 0) / m  # второй закон Ньютона, упрощенный 
    return [dxdt, dvdt] 
 
# Начальные условия 
x0 = 0.0  # начальное положение в метрах 
v0 = 0.0  # начальная скорость в м/с 
initial_conditions = [x0, v0] 
 
# Временной интервал для решения 
t_span = [0, 10]  # решаем от 0 до 10 секунд 
t_eval = np.linspace(t_span[0], t_span[1], 300)  # оценочные точки для графика 
 
# Решение дифференциального уравнения 
solution = solve_ivp(motion, t_span, initial_conditions, t_eval=t_eval, method='RK45') 
 
# Построение графиков 
plt.figure(figsize=(10, 5)) 
plt.subplot(1, 2, 1) 
plt.plot(solution.t, solution.y[0], label='x(t) - Position') 
plt.title('Position of the Piston over Time') 
plt.xlabel('Time (s)') 
plt.ylabel('Position (m)') 
plt.grid(True) 
plt.legend() 
 
plt.subplot(1, 2, 2) 
plt.plot(solution.t, solution.y[1], label='v(t) - Velocity') 
plt.title('Velocity of the Piston over Time') 
plt.xlabel('Time (s)') 
plt.ylabel('Velocity (m/s)') 
plt.grid(True) 
plt.legend() 
 
plt.tight_layout() 
plt.show()
