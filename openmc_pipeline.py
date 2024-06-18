import openmc
import numpy as np
import pandas as pd

import openmc
import numpy as np
import pandas as pd

# Функция для создания и запуска симуляции
def run_simulation(settings, materials, geometry, tallies, step, previous_results=None):
    settings.export_to_xml()
    materials.export_to_xml()
    geometry.export_to_xml()
    tallies.export_to_xml()
    
    openmc.run()
    
    sp = openmc.StatePoint('statepoint.100.h5')
    keff = sp.k_combined[0]
    keff_std = sp.k_combined[1]
    
    flux_tally = sp.get_tally(name='flux')
    flux_df = flux_tally.get_pandas_dataframe()
    phi_max = flux_df['mean'].max()
    
    fission_tally = sp.get_tally(name='fission')
    fission_df = fission_tally.get_pandas_dataframe()
    n_density = fission_df['mean'].sum()
    
    # Использование предыдущих результатов в качестве начальных условий
    if previous_results:
        previous_beta = previous_results[4]
        previous_heat_release = previous_results[5]
        previous_t_max = previous_results[6]
        previous_leaked_fraction = previous_results[7]

    return [step, keff, n_density, phi_max, beta, heat_release, t_max, leaked_fraction]

# Настройки для симуляции
settings = openmc.Settings()
settings.batches = 100  # Число циклов
settings.inactive = 10  # Число неактивных циклов
settings.particles = 1000  # Число частиц в каждом цикле

# Источник нейтронов
source_active = openmc.Source()
source_active.space = openmc.stats.Point((0, 0, 0))
source_active.angle = openmc.stats.Isotropic()
source_active.energy = openmc.stats.Discrete([2e6], [1])
settings.source = source_active

# Материалы
fuel = openmc.Material(name='UO2 Fuel')
fuel.add_element('U', 1, enrichment=4.25)
fuel.add_element('O', 2)
fuel.set_density('g/cm3', 10.29769)

moderator = openmc.Material(name='Graphite')
moderator.add_element('C', 1)
moderator.set_density('g/cm3', 1.7)

clad = openmc.Material(name='Zircaloy')
clad.add_element('Zr', 1)
clad.set_density('g/cm3', 6.55)

water = openmc.Material(name='Water')
water.add_element('H', 2)
water.add_element('O', 1)
water.set_density('g/cm3', 1.0)
water.add_s_alpha_beta('c_H_in_H2O')

materials = openmc.Materials([fuel, moderator, clad, water])

# Геометрия
radius_fuel = 0.39218
radius_clad = 0.45720
boundary = openmc.model.rectangular_prism(width=12.0, height=12.0, boundary_type='reflective')

fuel_or = openmc.ZCylinder(r=radius_fuel)
clad_or = openmc.ZCylinder(r=radius_clad)

fuel_region = -fuel_or
clad_region = +fuel_or & -clad_or
moderator_region = +clad_or & boundary

fuel_cell = openmc.Cell(fill=fuel, region=fuel_region)
clad_cell = openmc.Cell(fill=clad, region=clad_region)
moderator_cell = openmc.Cell(fill=moderator, region=moderator_region)

root_universe = openmc.Universe(cells=[fuel_cell, clad_cell, moderator_cell])
geometry = openmc.Geometry(root_universe)

# Счетчики (талли)
mesh = openmc.Mesh()
mesh.dimension = [100, 100, 1]
mesh.lower_left = [-6.0, -6.0, -1.0]
mesh.upper_right = [6.0, 6.0, 1.0]

flux_tally = openmc.Tally(name='flux')
flux_tally.filters = [openmc.MeshFilter(mesh)]
flux_tally.scores = ['flux']

fission_tally = openmc.Tally(name='fission')
fission_tally.filters = [openmc.MeshFilter(mesh)]
fission_tally.scores = ['fission']

tallies = openmc.Tallies([flux_tally, fission_tally])

# Первая симуляция с включенным источником
initial_result = run_simulation(settings, materials, geometry, tallies, 0)

# Цикл для выполнения последующих симуляций без источника и сохранения результатов
results = [initial_result]

for step in range(1, 12):
    settings.source = None  # Отключаем внешний источник нейтронов
    result = run_simulation(settings, materials, geometry, tallies, step)
    results.append(result)

# Сохранение результатов в DataFrame
columns = ['Ступень', 'Keff', 'n (нейтроны/см^3)', 'Phi_max (нейтроны/см^2/с)', 'beta (запазд. нейтроны)', 'тепловыделение (Вт)', 'T_max (K)', 'Leaked Fraction']
df_results = pd.DataFrame(results, columns=columns)
