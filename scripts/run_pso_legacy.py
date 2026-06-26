"""Research PSO driver for the PLAXIS tunnel-support model.

The numerical settings are preserved from the supplied experimental script.
Review them before starting a long PLAXIS run.
"""
#!/usr/bin/env python
# coding: utf-8

# In[1]:


from tunnel_support_optimization.modelo_tunel import *

initialize_plaxis()


# In[ ]:





# In[2]:


# Propiedades de los materiales
gammaUnsat1 = 14.51 # Peso Unitario del Suelo
ERef1 = 75000 # Módulo de Young del Suelo
nu1 = 0.3 # Relación Poisson del Suelo
cRef1 = 75 #Cohesión
phi1 = 30 #Ángulo de fricción

gammaUnsat2 = 20 # Peso Unitario del Suelo
ERef2 = 150000 # Módulo de Young del Suelo
nu2 = 0.3 # Relación Poisson del Suelo
cRef2 = 100 #Cohesión
phi2 = 30 #Ángulo de fricción

gammaUnsat3 = 24  # Peso Unitario del Suelo
Erm = 500000 # Módulo de Young del Suelo
nu3 = 0.3  # Relación Poisson del Suelo
AbsSigmaCI = 40000  # Relación de Compresión Uniaxial
mi = 8  # Parámetro de la Roca Intacta
GSI = 40 # Índice de Resistencia Geológica
Disturbance = 0.5  # Factor de Perturbación D

EA1= 1647023.8095238097
EI= 2066.835088522588
StructNu= 0.275
w=2.73666

phase0_s, x_point = generar_modelo_plaxis(gammaUnsat1,gammaUnsat2,gammaUnsat3,ERef1,ERef2,\
                                          Erm,nu1,nu2,nu3,cRef1,cRef2,phi1,phi2,AbsSigmaCI, mi, GSI, Disturbance,\
                                          w, EA1, EI, StructNu)


# In[3]:


import time
import numpy as np
import pyswarms as ps
from pyswarms.utils.functions import single_obj as fx

# Captura el tiempo inicial
inicio = time.time()

# Definir constantes globales
shotcreteCompressiveStrength = 32800.0  
shotcretePoissonRatio = 0.21  
shotcreteTensileStrength = 3280   
shotcreteUnitWeight = 27.0
shotcreteYoungModulus = 14000000.0   

# Definir límites de los parámetros para PSO
bounds = (np.array([0.10]), np.array([0.50]))  # shotcreteThickness variará entre 0.05 y 0.50

# Definir la lista de datos
data = [
    [78.00,float(2.00),0.00247,0.00000470,200000000.00,0.3,0.106,355000.00,355000.00],
    [78.00,float(2.00),0.00323,0.00000887,200000000.00,0.3,0.127,355000.00,355000.00],
    [78.00,float(2.00),0.00357,0.00001091,200000000.00,0.3,0.131,355000.00,355000.00],
    [78.00,float(2.00),0.00286,0.00001211,200000000.00,0.3,0.152,355000.00,355000.00],
    [78.00,float(2.00),0.00379,0.00001723,200000000.00,0.3,0.157,355000.00,355000.00],
    [78.00,float(2.00),0.00474,0.00002223,200000000.00,0.3,0.162,355000.00,355000.00],
    [78.00,float(2.00),0.00457,0.00003446,200000000.00,0.3,0.201,355000.00,355000.00],
    [78.00,float(2.00),0.00532,0.00004079,200000000.00,0.3,0.205,355000.00,355000.00],
    [78.00,float(2.00),0.00589,0.00004579,200000000.00,0.3,0.203,355000.00,355000.00],
    [78.00,float(2.00),0.00665,0.00005286,200000000.00,0.3,0.206,355000.00,355000.00],
    [78.00,float(2.00),0.00755,0.00006077,200000000.00,0.3,0.210,355000.00,355000.00],
    [78.00,float(2.00),0.00910,0.00007659,200000000.00,0.3,0.216,355000.00,355000.00],
    [78.00,float(2.00),0.01103,0.00009490,200000000.00,0.3,0.222,355000.00,355000.00],
    [78.00,float(2.00),0.01271,0.00011321,200000000.00,0.3,0.229,355000.00,355000.00],
    [78.00,float(2.00),0.00626,0.00007076,200000000.00,0.3,0.247,355000.00,355000.00],
    [78.00,float(2.00),0.00742,0.00008699,200000000.00,0.3,0.252,355000.00,355000.00],
    [78.00,float(2.00),0.00858,0.00010323,200000000.00,0.3,0.257,355000.00,355000.00],
    [78.00,float(2.00),0.00929,0.00011321,200000000.00,0.3,0.253,355000.00,355000.00],
    [78.00,float(2.00),0.01019,0.00012612,200000000.00,0.3,0.256,355000.00,355000.00],
    [78.00,float(2.00),0.01290,0.00016400,200000000.00,0.3,0.264,355000.00,355000.00],
    [78.00,float(2.00),0.01458,0.00018938,200000000.00,0.3,0.269,355000.00,355000.00],
    [78.00,float(2.00),0.01671,0.00022227,200000000.00,0.3,0.275,355000.00,355000.00],
    [78.00,float(2.00),0.01897,0.00025931,200000000.00,0.3,0.282,355000.00,355000.00],
    [78.00,float(2.00),0.02123,0.00029802,200000000.00,0.3,0.289,355000.00,355000.00],
    [78.00,float(2.00),0.01007,0.00017690,200000000.00,0.3,0.306,355000.00,355000.00],
    [78.00,float(2.00),0.01097,0.00019771,200000000.00,0.3,0.310,355000.00,355000.00],
    [78.00,float(2.00),0.01232,0.00022185,200000000.00,0.3,0.308,355000.00,355000.00],
    [78.00,float(2.00),0.01361,0.00024850,200000000.00,0.3,0.310,355000.00,355000.00],
    [78.00,float(2.00),0.01497,0.00027554,200000000.00,0.3,0.314,355000.00,355000.00],
    [78.00,float(2.00),0.01652,0.00030801,200000000.00,0.3,0.318,355000.00,355000.00],
    [78.00,float(2.00),0.01819,0.00034672,200000000.00,0.3,0.323,355000.00,355000.00],
    [78.00,float(2.00),0.02013,0.00038834,200000000.00,0.3,0.327,355000.00,355000.00],
    [78.00,float(2.00),0.02278,0.00044537,200000000.00,0.3,0.333,355000.00,355000.00],
    [78.00,float(2.00),0.02574,0.00051613,200000000.00,0.3,0.341,355000.00,355000.00],
    [78.00,float(2.00),0.02884,0.00059521,200000000.00,0.3,0.348,355000.00,355000.00],
    [78.00,float(2.00),0.03226,0.00068678,200000000.00,0.3,0.356,355000.00,355000.00],
    [78.00,float(2.00),0.03600,0.00078667,200000000.00,0.3,0.365,355000.00,355000.00],
    [78.00,float(2.00),0.03987,0.00089073,200000000.00,0.3,0.374,355000.00,355000.00],
    [78.00,float(2.00),0.04368,0.00100728,200000000.00,0.3,0.382,355000.00,355000.00],
    [78.00,float(2.00),0.04781,0.00113215,200000000.00,0.3,0.391,355000.00,355000.00]
]

# Convertir en arreglo numpy
data = np.array(data)

# Crear un DataFrame vacío globalmente para almacenar los datos
df_results = pd.DataFrame(columns=[
    'phase0_s', 'x_point', 'shotcreteCompressiveStrength', 'shotcretePoissonRatio',
    'shotcreteTensileStrength', 'shotcreteThickness', 'shotcreteUnitWeight',
    'shotcreteYoungModulus', 'steelSetArea', 'steelSetCompressiveStrength',
    'steelSetInertia', 'steelSetPoissonRatio', 'steelSetSectionDepth', 'steelSetSpacing',
    'steelSetTensileStrength', 'steelSetYoungModulus', 'steelUnitWeight',
    'utot_values', 'utot_values2', 'w', 'EA1', 'EI', 'StructNu', 'porcentajepyswarm'
])

def calculate_properties(steelUnitWeight, steelSetSpacing, steelSetArea, steelSetInertia, steelSetYoungModulus, steelSetPoissonRatio, steelSetSectionDepth, steelSetCompressiveStrength, steelSetTensileStrength, shotcreteThickness):
    # Cálculo de d_st, d_sh, k_st, k_sh
    d_st = (steelSetYoungModulus * steelSetArea) / (1 - steelSetPoissonRatio ** 2)
    d_sh = (shotcreteYoungModulus * shotcreteThickness) / (1 - shotcretePoissonRatio ** 2)

    k_st = (steelSetYoungModulus * steelSetInertia) / (1 - steelSetPoissonRatio ** 2)
    k_sh = (shotcreteYoungModulus * shotcreteThickness ** 3) / (12 * (1 - shotcretePoissonRatio ** 2))

    # Cálculo de EA1, EI, StructNu, w
    EA1 = d_st / steelSetSpacing + d_sh
    EI = k_st / steelSetSpacing + k_sh
    StructNu = 0.275
    w = shotcreteUnitWeight * shotcreteThickness + steelUnitWeight * steelSetArea / steelSetSpacing

    return EA1, EI, StructNu, w

def fitness_func(params):
    calculated_values = []  # Para almacenar todos los valores calculados de cada iteración

    while len(params) > 0:
        # Extraer y procesar el primer valor de los parámetros
        first_element = params[0]
        param0 = round(first_element[0], 2)
        shotcreteThickness = param0
        params = params[1:]  # Pasar al siguiente valor en params

        # Seleccionar un subconjunto aleatorio de data para este valor de param0
        selected_rows = np.random.choice(len(data), size=1, replace=False)

        for i in range(len(selected_rows)):
            row = data[selected_rows[i]]
            steelUnitWeight, steelSetSpacing, steelSetArea, steelSetInertia, steelSetYoungModulus, steelSetPoissonRatio, \
            steelSetSectionDepth, steelSetCompressiveStrength, steelSetTensileStrength = row

            # Calcular propiedades con el valor actual de shotcreteThickness
            EA1, EI, StructNu, w = calculate_properties(
                steelUnitWeight, steelSetSpacing, steelSetArea, steelSetInertia, 
                steelSetYoungModulus, steelSetPoissonRatio, steelSetSectionDepth, 
                steelSetCompressiveStrength, steelSetTensileStrength, shotcreteThickness)

            calculated_values.append([steelUnitWeight, steelSetSpacing, steelSetArea, steelSetInertia, 
                steelSetYoungModulus, steelSetPoissonRatio, steelSetSectionDepth, 
                steelSetCompressiveStrength, steelSetTensileStrength, EA1, EI, 
                StructNu, w, shotcreteThickness])

    for calculated_row in calculated_values:
        steelUnitWeight, steelSetSpacing, steelSetArea, steelSetInertia, steelSetYoungModulus, steelSetPoissonRatio, \
        steelSetSectionDepth, steelSetCompressiveStrength, steelSetTensileStrength, EA1, EI, StructNu, w, shotcreteThickness = calculated_row

        s_o.close()
        
        utot = []
        utot2 = []

        sostenimiento = generar_sostenimiento(phase0_s, x_point, shotcreteCompressiveStrength, shotcretePoissonRatio,
                                              shotcreteTensileStrength, shotcreteThickness, shotcreteUnitWeight,
                                              shotcreteYoungModulus, steelSetArea, steelSetCompressiveStrength,
                                              steelSetInertia, steelSetPoissonRatio, steelSetSectionDepth, steelSetSpacing,
                                              steelSetTensileStrength, steelSetYoungModulus, steelUnitWeight, utot, utot2,
                                              w, EA1, EI, StructNu)

        # Agregar los resultados a df_results
        new_data = pd.DataFrame([{
            'phase0_s': phase0_s,
            'x_point': x_point,
            'shotcreteCompressiveStrength': shotcreteCompressiveStrength,
            'shotcretePoissonRatio': shotcretePoissonRatio,
            'shotcreteTensileStrength': shotcreteTensileStrength,
            'shotcreteThickness': shotcreteThickness,
            'shotcreteUnitWeight': shotcreteUnitWeight,
            'shotcreteYoungModulus': shotcreteYoungModulus,
            'steelSetArea': steelSetArea,
            'steelSetCompressiveStrength': steelSetCompressiveStrength,
            'steelSetInertia': steelSetInertia,
            'steelSetPoissonRatio': steelSetPoissonRatio,
            'steelSetSectionDepth': steelSetSectionDepth,
            'steelSetSpacing': steelSetSpacing,
            'steelSetTensileStrength': steelSetTensileStrength,
            'steelSetYoungModulus': steelSetYoungModulus,
            'steelUnitWeight': steelUnitWeight,
            'utot_values': utot,
            'utot_values2': utot2,
            'w': w,
            'EA1': EA1,
            'EI': EI,
            'StructNu': StructNu,
            'porcentajepyswarm': sostenimiento
        }])

        global df_results
        df_results = pd.concat([df_results, new_data], ignore_index=True)
        
        # Guardar el DataFrame en un archivo CSV después de agregar los resultados
        df_results.to_csv(str(settings.results_dir / 'resultadosNvoMaterialGSI2Ana400.csv'), index=False, encoding='utf-8')
    
    # Deja el sostenimiento para que el algoritmo maximice la función de fitness
    print("Los valores de los parámetros en esta iteración son:", param0)
    print("El valor de sostenimiento es:", sostenimiento)
    # Retornar el valor del sostenimiento como fitness score
    return sostenimiento

# Definir parámetros de la optimización
options = {'c1': 0.5, 'c2': 0.3, 'w':0.9, 'nan_policy':'omit'}

# Crear instancia de optimizador PSO
optimizer = ps.single.GlobalBestPSO(n_particles=1, dimensions=1, options=options, bounds=bounds)

# Ejecutar el optimizador PSO
best_cost, best_pos = optimizer.optimize(fitness_func, iters=1)

# Obtener la cadena de valores de los parámetros y el valor de sostenimiento óptimos
best_pos = np.array([best_pos])
fitness_func_result = fitness_func(best_pos)
optimal_result_str = fitness_func_result

# Imprimir resultados
print("Los valores óptimos de los parámetros son: ", best_pos)
print("El valor óptimo de la función de fitness es: ", best_cost)
print("La cadena de valores óptimos es: ", optimal_result_str)

# Captura el tiempo final
fin = time.time()

# Calcula el tiempo transcurrido en segundos
duracion = fin - inicio

# Convierte a horas, minutos y segundos
horas = int(duracion // 3600)
minutos = int((duracion % 3600) // 60)
segundos = duracion % 60

# Muestra el resultado formateado
print(f"El proceso tomó {horas} horas, {minutos} minutos y {segundos:.4f} segundos.")


# In[4]:


import pandas as pd

# Cargar el archivo CSV
df = pd.read_csv(str(settings.results_dir / 'resultadosNvoMaterialGSI2Ana400.csv'))

# Seleccionar las columnas 'porcentajepyswarm' y 'shotcreteThickness'
tabla_final = df[['porcentajepyswarm', 'shotcreteThickness']]

# Mostrar la tabla completa con los valores de porcentajepyswarm y shotcreteThickness
print(tabla_final)

# Seleccionar las columnas relevantes
columns = ['porcentajepyswarm', 'shotcreteThickness']

# Filtrar los datos donde porcentajepyswarm sea igual a 1.0
df_filtered = df[df['porcentajepyswarm'] < 2000]

# Crear una nueva tabla con los valores filtrados de porcentajepyswarm y shotcreteThickness
tabla_final2 = df_filtered[['porcentajepyswarm', 'shotcreteThickness']]

# Mostrar la tabla final
print(tabla_final2)


# In[5]:


import pandas as pd

# Cargar los archivos CSV
resultados_df = pd.read_csv(str(settings.results_dir / 'resultadosNvoMaterialGSI2Ana400.csv'))
sostenimiento_df = pd.read_csv(str(settings.project_root / 'data' / 'input' / 'NombresSostenimiento.csv'))

# Agregar una columna 'ID' para numerar las filas
resultados_df['ID'] = resultados_df.index + 1  # Numerar las filas comenzando desde 1

# Inicializar una nueva columna para almacenar el nombre del sostenimiento
resultados_df['Sostenimiento'] = None

# Filas clave que se utilizarán para la comparación
columnas_comparacion = ['steelUnitWeight', 'steelSetSpacing', 'steelSetArea', 
                        'steelSetInertia', 'steelSetYoungModulus', 'steelSetPoissonRatio', 
                        'steelSetSectionDepth', 'steelSetCompressiveStrength', 
                        'steelSetTensileStrength']

# Iterar sobre cada fila de str(settings.results_dir / 'resultados.csv')
for idx, row in resultados_df.iterrows():
    # Buscar una coincidencia en str(settings.project_root / 'data' / 'input' / 'NombresSostenimiento.csv')
    match = sostenimiento_df[
        (sostenimiento_df['steelUnitWeight'] == row['steelUnitWeight']) &
        (sostenimiento_df['steelSetSpacing'] == row['steelSetSpacing']) &
        (sostenimiento_df['steelSetArea'] == row['steelSetArea']) &
        (sostenimiento_df['steelSetInertia'] == row['steelSetInertia']) &
        (sostenimiento_df['steelSetYoungModulus'] == row['steelSetYoungModulus']) &
        (sostenimiento_df['steelSetPoissonRatio'] == row['steelSetPoissonRatio']) &
        (sostenimiento_df['steelSetSectionDepth'] == row['steelSetSectionDepth']) &
        (sostenimiento_df['steelSetCompressiveStrength'] == row['steelSetCompressiveStrength']) &
        (sostenimiento_df['steelSetTensileStrength'] == row['steelSetTensileStrength'])
    ]

    # Si se encuentra una coincidencia, asignar el nombre del sostenimiento
    if not match.empty:
        resultados_df.at[idx, 'Sostenimiento'] = match.iloc[0]['Sostenimiento']

# Guardar el DataFrame actualizado en un nuevo archivo CSV
resultados_df.to_csv(str(settings.results_dir / 'resultados_actualizadosNvoMaterialGSI2Ana400.csv'), index=False)

print("Actualización completada. El archivo str(settings.results_dir / 'resultados_actualizadosNvoMaterialGSI2Ana400.csv') ha sido guardado.")


# In[6]:


import pandas as pd
import matplotlib.pyplot as plt

# Cargar los archivos CSV
df1 = pd.read_csv(str(settings.results_dir / 'resultados_actualizadosNvoMaterialGSI2Ana400.csv'))

# Añadir una columna para identificar la fuente de cada DataFrame
df1['source'] = 'PSO200'

# Combinar los DataFrames
df_original = pd.concat([df1])

# Seleccionar las columnas de interés
df = df_original[['ID', 'shotcreteThickness', 'utot_values', 'porcentajepyswarm', 'Sostenimiento', 'source']].copy()

# Filtrar solo los valores menores a 2000 en 'porcentajepyswarm'
df = df[df['porcentajepyswarm'] < 2000]

# Definir un diccionario para el mapeo de sostenimiento a valores numéricos
mapeo_sostenimiento = {
    '102x19.4': 0,
    '127x23.7': 1,
    '127x28.1': 2,
    '152x22.4': 3,
    '152x29.7': 4,
    '152x37.2': 5,
    '203x35.9': 6,
    '203x41.8': 7,
    '203x46.2': 8,
    '203x52.2': 9,
    '203x59.3': 10,
    '203x71.4': 11,
    '203x86.6': 12,
    '203x99.8': 13,
    '254x49.2': 14,
    '254x58.2': 15,
    '254x67.4': 16,
    '254x72.9': 17,
    '254x80': 18,
    '254x89.1': 19,
    '254x101.3': 20,
    '254x114.5': 21,
    '254x131.2': 22,
    '254x148.9': 23,
    '254x166.6': 24,
    '305x79': 25,
    '305x86.1': 26,
    '305x96.7': 27,
    '305x106.9': 28,
    '305x117.5': 29,
    '305x129.7': 30,
    '305x142.8': 31,
    '305x158': 32,
    '305x178.8': 33,
    '305x202.1': 34,
    '305x226.4': 35,
    '305x253.2': 36,
    '305x282.6': 37,
    '305x313': 38,
    '305x342.9': 39
}

# Crear una nueva columna 'Sostenimiento_Numerico' usando el mapeo
df['Sostenimiento_Numerico'] = df['Sostenimiento'].map(mapeo_sostenimiento)

# Limpiar los valores de utot_values
df['utot_values'] = df['utot_values'].str.strip("[]").astype(float)

# Asegurarse de que las columnas sean numéricas, forzando conversión
df['utot_values'] = pd.to_numeric(df['utot_values'], errors='coerce')

# Eliminar filas con valores NaN
df = df.dropna(subset=['utot_values', 'Sostenimiento_Numerico'])

# Multiplicar los valores de utot_values por 1000
df['utot_values'] = df['utot_values'] * 1000

# Obtener los 10 o 20 IDs con los menores valores de utot_values
num_menores = 10  # Cambia a 20 si deseas los 20 valores más bajos
valores_bajos = df.nsmallest(num_menores, 'utot_values')

# Imprimir los IDs
print("IDs de los", num_menores, "valores más bajos de utot_values:")
print(valores_bajos[['ID', 'shotcreteThickness', 'Sostenimiento']])

# Crear el gráfico de dispersión 2D
plt.figure(figsize=(10, 6))

# Colores para los puntos
colores_puntos = {'PSO200': 'DarkOrange'}

# Usar la columna 'source' para agrupar los datos y graficar
for archivo, grupo in df.groupby('source'):
    plt.scatter(grupo['Sostenimiento_Numerico'], grupo['utot_values'], color=colores_puntos[archivo], label=archivo)
    
    # Añadir la anotación de los índices de fila (ID) al lado de cada punto
    for i, row in grupo.iterrows():
        # Desplazamiento basado en si el índice es par o impar
        offset_y = 5 if i % 2 == 0 else -10
        offset_x = 5 if i % 3 == 0 else -5
        plt.annotate(str(int(row['ID'])), (row['Sostenimiento_Numerico'], row['utot_values']),
                     textcoords="offset points", xytext=(offset_x, offset_y), ha='center', fontsize=6, rotation=45)

# Establecer las etiquetas del eje X con los nombres de sostenimiento
plt.xticks(ticks=list(mapeo_sostenimiento.values()), labels=list(mapeo_sostenimiento.keys()), rotation=45, ha='right')

# Añadir etiquetas a los ejes y título
plt.xlabel('Perfiles IR (Sostenimiento)')
plt.ylabel('Deformación total (utot_values)')
plt.title('Gráfico de Deformación Total vs Perfiles por Análisis PSO')


# Mover la leyenda fuera del gráfico
plt.legend(title='Análisis PSO', loc='center left', bbox_to_anchor=(1, 0.5))

# Mostrar el gráfico
plt.grid(True)
plt.tight_layout()  # Ajusta el diseño para que las etiquetas no se corten
plt.show()


# In[7]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Cargar los archivos CSV
df1 = pd.read_csv(str(settings.results_dir / 'resultados_actualizadosNvoMaterialGSI2Ana400.csv'))

# Añadir una columna para identificar la fuente de cada DataFrame
df1['source'] = 'PSO200'

# Combinar los DataFrames
df_original = pd.concat([df1])

# Seleccionar las columnas de interés
df = df_original[['ID', 'shotcreteThickness', 'utot_values', 'porcentajepyswarm', 'Sostenimiento', 'source']].copy()

# Filtrar solo los valores menores a 2000 en 'porcentajepyswarm'
df = df[df['porcentajepyswarm'] < 2000]

# Definir un diccionario para el mapeo de sostenimiento a valores numéricos
mapeo_sostenimiento = {
    '102x19.4': 0, '127x23.7': 1, '127x28.1': 2, '152x22.4': 3, '152x29.7': 4, '152x37.2': 5,
    '203x35.9': 6, '203x41.8': 7, '203x46.2': 8, '203x52.2': 9, '203x59.3': 10, '203x71.4': 11,
    '203x86.6': 12, '203x99.8': 13, '254x49.2': 14, '254x58.2': 15, '254x67.4': 16, '254x72.9': 17,
    '254x80': 18, '254x89.1': 19, '254x101.3': 20, '254x114.5': 21, '254x131.2': 22, '254x148.9': 23,
    '254x166.6': 24, '305x79': 25, '305x86.1': 26, '305x96.7': 27, '305x106.9': 28, '305x117.5': 29,
    '305x129.7': 30, '305x142.8': 31, '305x158': 32, '305x178.8': 33, '305x202.1': 34,
    '305x226.4': 35, '305x253.2': 36, '305x282.6': 37, '305x313': 38, '305x342.9': 39
}

# Crear una nueva columna 'Sostenimiento_Numerico' usando el mapeo
df['Sostenimiento_Numerico'] = df['Sostenimiento'].map(mapeo_sostenimiento)

# Asegurarse de que las columnas sean numéricas, forzando conversión
df['shotcreteThickness'] = pd.to_numeric(df['shotcreteThickness'], errors='coerce')

# Limpiar los valores de utot_values
df['utot_values'] = df['utot_values'].str.strip("[]").astype(float)

# Eliminar filas con valores NaN
df = df.dropna(subset=['shotcreteThickness', 'Sostenimiento_Numerico'])

# Crear el gráfico de dispersión 2D
plt.figure(figsize=(10, 6))

# Colores para los puntos
colores_puntos = {'PSO200': 'DarkOrange', 'PSO400': 'MediumSeaGreen', 'PSO600': 'RoyalBlue', 'PSO800': 'GoldenRod'}

# Colores para las líneas de solución
line_colors = {
    'PSO200': 'crimson',        # Color rojo
    'PSO400': 'dodgerblue',     # Color azul
    'PSO600': 'limegreen',      # Color verde lima
    'PSO800': 'goldenrod'       # Color dorado
}

# Obtener los 5 IDs con los menores valores de utot_values
num_menores = 5  # Cambia a 5 si deseas los 5 valores más bajos
valores_bajos = df.nsmallest(num_menores, 'utot_values')

# Extraer los IDs de los valores más bajos
ids_a_marcar = valores_bajos['ID'].tolist()

# Imprimir los IDs con sus correspondientes valores
print("IDs de los", num_menores, "valores más bajos de utot_values:")
print(valores_bajos[['ID', 'shotcreteThickness', 'Sostenimiento']])

# Usar la columna 'source' para agrupar los datos y graficar
for archivo, grupo in df.groupby('source'):
    plt.scatter(grupo['Sostenimiento_Numerico'], grupo['shotcreteThickness'], color=colores_puntos[archivo], label=archivo)
    
    # Agregar el número de ID solo si está en ids_a_marcar
    for i, row in grupo.iterrows():
        if int(row['ID']) in ids_a_marcar:
            plt.annotate(str(int(row['ID'])), (row['Sostenimiento_Numerico'], row['shotcreteThickness']),
                         textcoords="offset points", xytext=(5, 5), ha='center', fontsize=8, rotation=45)

# Marcar los IDs en el gráfico
for id_marcado in ids_a_marcar:
    # Obtener la fila correspondiente al ID
    fila = df[df['ID'] == id_marcado]
    if not fila.empty:
        plt.scatter(fila['Sostenimiento_Numerico'], fila['shotcreteThickness'], 
                    color='red', s=100, edgecolor='black', label=f'ID {id_marcado}')

# Graficar la línea recta del último valor de shotcreteThickness para cada grupo
for archivo, grupo in df_original.groupby('source'):
    ultimo_valor = grupo['shotcreteThickness'].iloc[-1]  # Último valor de shotcreteThickness
    plt.axhline(y=ultimo_valor, color=line_colors[archivo], linestyle='-', linewidth=2, label=f'{archivo} solución')    

# Establecer las etiquetas del eje X con los nombres de sostenimiento
plt.xticks(ticks=list(mapeo_sostenimiento.values()), labels=list(mapeo_sostenimiento.keys()), rotation=45, ha='right')

# Añadir etiquetas a los ejes y título
plt.xlabel('Perfiles IR (Sostenimiento)')
plt.ylabel('Espesor (shotcreteThickness)')
plt.title('Gráfico de Espesor vs Perfiles por Análisis PSO')

# Mover la leyenda fuera del gráfico
plt.legend(title='Análisis PSO', loc='center left', bbox_to_anchor=(1, 0.5))

# Mostrar el gráfico
plt.grid(True)
plt.tight_layout()  # Ajusta el diseño para que las etiquetas no se corten
plt.show()



# In[8]:


import pandas as pd
import plotly.graph_objects as go

# Cargar los archivos CSV
df1 = pd.read_csv(str(settings.results_dir / 'resultados_actualizadosNvoMaterialGSI2Ana400.csv'))
df2 = pd.read_csv(str(settings.results_dir / 'resultados_actualizados400.csv'))
df3 = pd.read_csv(str(settings.results_dir / 'resultados_actualizados600.csv'))
df4 = pd.read_csv(str(settings.results_dir / 'resultados_actualizados800.csv'))

# Añadir una columna para identificar la fuente de cada DataFrame
df1['source'] = 'PSO200'
df2['source'] = 'PSO400'
df3['source'] = 'PSO600'
df4['source'] = 'PSO800'

# Combinar los DataFrames
df_resultados = pd.concat([df1, df2, df3, df4])

# Seleccionar las columnas de interés
df = df_resultados[['ID', 'shotcreteThickness', 'utot_values', 'porcentajepyswarm', 'Sostenimiento', 'source']].copy()

# Filtrar valores de 'PSO200' y porcentajepyswarm == 100
df = df[(df['source'] == 'PSO200') & (df['porcentajepyswarm'] <2000 )]

# Extraer el segundo número de la columna 'Sostenimiento' después de la "x"
df['Sostenimiento'] = df['Sostenimiento'].astype(str).str.split('x').str[1].astype(float)

# Asegurarse de que las columnas sean numéricas
df['shotcreteThickness'] = pd.to_numeric(df['shotcreteThickness'], errors='coerce')

# Extraer el valor de la lista de 'utot_values'
df['utot_values'] = df['utot_values'].apply(lambda x: float(x.strip('[]')) if isinstance(x, str) else x)

# Asegurarse de que 'utot_values' sea numérico
df['utot_values'] = pd.to_numeric(df['utot_values'], errors='coerce')

# Eliminar filas con valores NaN
df = df.dropna(subset=['shotcreteThickness', 'Sostenimiento', 'utot_values'])

# Obtener los 5 IDs con los menores valores de 'utot_values'
valores_bajos = df.nsmallest(5, 'utot_values')
ids_a_marcar = valores_bajos['ID'].tolist()

# Crear una figura 3D interactiva con Plotly
fig = go.Figure()

# Graficar todos los puntos de PSO200
fig.add_trace(go.Scatter3d(
    x=df['shotcreteThickness'],
    y=df['Sostenimiento'],
    z=df['utot_values'],
    mode='markers',
    marker=dict(size=5, color='DarkOrange'),
    name='PSO200'
))

# Marcar los puntos con los IDs seleccionados en un color distinto (rojo)
df_marcados = df[df['ID'].isin(ids_a_marcar)]
fig.add_trace(go.Scatter3d(
    x=df_marcados['shotcreteThickness'],
    y=df_marcados['Sostenimiento'],
    z=df_marcados['utot_values'],
    mode='markers',
    marker=dict(size=8, color='red', symbol='circle'),
    name='IDs Marcados'
))

# Añadir etiquetas a los ejes
fig.update_layout(
    scene=dict(
        xaxis_title='Espesor (Shotcrete Thickness)',
        yaxis_title='Perfiles IR (Sostenimiento)',
        zaxis_title='Deformación Final (utot_values)'
    ),
    title="Gráfico 3D de PSO200 con IDs Marcados",
    legend_title="Análisis"
)

# Mostrar la figura interactiva
fig.show()


# In[ ]:




