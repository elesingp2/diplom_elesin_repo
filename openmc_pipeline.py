# Шаг 1: Импорт необходимых библиотек
# Импортируем библиотеку OpenMC для моделирования ядерных реакторов,
# библиотеку matplotlib.pyplot для визуализации результатов и numpy для работы с массивами данных.
import openmc
import matplotlib.pyplot as plt
import numpy as np

# Шаг 2: Определение материалов
# Определяем материалы, которые будут использоваться в симуляции: топливо UO2, графит (замедлитель), циркалой (оболочка твэлов) и вода (охладитель).

# Топливо UO2
fuel = openmc.Material(name='UO2 Fuel')
fuel.add_element('U', 1, enrichment=4.25)  # Уран с обогащением 4.25%
fuel.add_element('O', 2)
fuel.set_density('g/cm3', 10.29769)

# Графит (замедлитель)
moderator = openmc.Material(name='Graphite')
moderator.add_element('C', 1)
moderator.set_density('g/cm3', 1.7)

# Циркалой (оболочка твэлов)
clad = openmc.Material(name='Zircaloy')
clad.add_element('Zr', 1)
clad.set_density('g/cm3', 6.55)

# Вода (охладитель)
water = openmc.Material(name='Water')
water.add_element('H', 2)
water.add_element('O', 1)
water.set_density('g/cm3', 1.0)
water.add_s_alpha_beta('c_H_in_H2O')

# Сбор всех материалов в объект Materials и экспорт в XML
materials = openmc.Materials([fuel, moderator, clad, water])
materials.export_to_xml()

# Шаг 3: Определение геометрии
# Определяем геометрию реактора с использованием цилиндрических границ для топлива и оболочки,
# а также прямоугольной призмы для граничных условий.

# Радиусы и шаг
radius_fuel = 0.39218
radius_clad = 0.45720
pitch = 1.26

# Цилиндрические границы для топлива и оболочки
fuel_or = openmc.ZCylinder(r=radius_fuel)
clad_or = openmc.ZCylinder(r=radius_clad)

# Прямоугольная призма для граничных условий
boundary = openmc.model.rectangular_prism(width=12.0, height=12.0, boundary_type='reflective')

# Области для ячеек
fuel_region = -fuel_or
clad_region = +fuel_or & -clad_or
moderator_region = +clad_or & boundary

# Создание ячеек
fuel_cell = openmc.Cell(fill=fuel, region=fuel_region)
clad_cell = openmc.Cell(fill=clad, region=clad_region)
moderator_cell = openmc.Cell(fill=moderator, region=moderator_region)

# Создание вселенной (универсальной области)
root_universe = openmc.Universe(cells=[fuel_cell, clad_cell, moderator_cell])
geometry = openmc.Geometry(root_universe)
geometry.export_to_xml()

# Шаг 4: Настройка параметров симуляции
# Определяем параметры симуляции: число циклов, неактивных циклов и частиц в каждом цикле.
# Задаем источники нейтронов, расположенные по краям реактора.

settings = openmc.Settings()
settings.batches = 100  # Число циклов
settings.inactive = 10  # Число неактивных циклов
settings.particles = 1000  # Число частиц в каждом цикле

# Определение источников по краям реактора
edge_sources = [
    openmc.stats.Point((-6, -6, 0)),
    openmc.stats.Point((6, -6, 0)),
    openmc.stats.Point((-6, 6, 0)),
    openmc.stats.Point((6, 6, 0))
]
sources = [openmc.Source(space=point) for point in edge_sources]
settings.source = sources

settings.export_to_xml()

# Шаг 5: Определение счетчиков (талли)
# Создаем счетчики для плотности потока нейтронов и скорости делений с использованием сетки.

# Создание сетки
mesh = openmc.Mesh()
mesh.dimension = [100, 100, 1]
mesh.lower_left = [-6.0, -6.0, -1.0]
mesh.upper_right = [6.0, 6.0, 1.0]

# Счетчик плотности потока нейтронов
flux_tally = openmc.Tally(name='flux')
flux_tally.filters = [openmc.MeshFilter(mesh)]
flux_tally.scores = ['flux']

# Счетчик делений
fission_tally = openmc.Tally(name='fission')
fission_tally.filters = [openmc.MeshFilter(mesh)]
fission_tally.scores = ['fission']

# Экспорт счетчиков в XML
tallies = openmc.Tallies([flux_tally, fission_tally])
tallies.export_to_xml()

# Шаг 6: Запуск симуляции
# Выполняем симуляцию с помощью команды openmc.run().
openmc.run()

# Шаг 7: Обработка результатов
# Получаем данные из файла statepoint.h5 и преобразуем их в формат DataFrame для дальнейшего анализа.

sp = openmc.StatePoint('statepoint.100.h5')

flux = sp.get_tally(name='flux')
flux_df = flux.get_pandas_dataframe()

fission = sp.get_tally(name='fission')
fission_df = fission.get_pandas_dataframe()
# Шаг 8: Визуализация результатов
# Строим графики распределения плотности потока нейтронов и скорости делений.

# Плотность потока нейтронов
flux_values = flux_df['mean'].values.reshape(mesh.dimension)
plt.imshow(flux_values, origin='lower', cmap='viridis')
plt.colorbar(label='Neutron Flux')
plt.title('Neutron Flux Distribution')
plt.xlabel('X')
plt.ylabel('Y')
plt.show()

# Скорость делений
fission_values = fission_df['mean'].values.reshape(mesh.dimension)
plt.imshow(fission_values, origin='lower', cmap='inferno')
plt.colorbar(label='Fission Rate')
plt.title('Fission Rate Distribution')
plt.xlabel('X')
plt.ylabel('Y')
plt.show()
