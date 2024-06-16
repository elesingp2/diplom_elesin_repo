# Построение графиков по радиусу и по времени

# График температуры в зависимости от радиуса для нескольких моментов времени
times_to_plot = [0.1, 1, 5, 10]  # Моменты времени для графика по радиусу
time_indices = [np.abs(t - time).argmin() for time in times_to_plot]

plt.figure(figsize=(10, 6))
for i, time_index in enumerate(time_indices):
    plt.plot(r, sol.y[:, time_index], label=f't = {times_to_plot[i]} с')
plt.xlabel('Расстояние от центра (м)')
plt.ylabel('Температура (К)')
plt.title('Зависимость температуры от радиуса в разные моменты времени')
plt.legend()
plt.grid(True)
plt.show()

# График температуры в зависимости от времени для нескольких радиусов
radii_to_plot = [0, 0.05, 0.1, 0.2]  # Радиусы для графика по времени
radius_indices = [np.abs(r - radius).argmin() for radius in radii_to_plot]

plt.figure(figsize=(10, 6))
for i, radius_index in enumerate(radius_indices):
    plt.plot(t, sol.y[radius_index, :], label=f'r = {radii_to_plot[i]} м')
plt.xlabel('Время (с)')
plt.ylabel('Температура (К)')
plt.title('Зависимость температуры от времени для разных радиусов')
plt.legend()
plt.grid(True)
plt.show()
