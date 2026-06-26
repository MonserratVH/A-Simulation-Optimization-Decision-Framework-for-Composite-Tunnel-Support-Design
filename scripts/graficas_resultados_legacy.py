#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Cargar los archivos CSV
df1 = pd.read_csv('resultados_actualizados200Nvo.csv')
df2 = pd.read_csv('resultados_actualizados400Nvo.csv')
df3 = pd.read_csv('resultados_actualizados600Nvo.csv')

# Añadir una columna para identificar la fuente de cada DataFrame
df1['source'] = 'PSO200'
df2['source'] = 'PSO400'
df3['source'] = 'PSO600'
#df4['source'] = 'PSO800'

# Combinar los DataFrames
#df_original = pd.concat([df1, df2, df3, df4])
df_original = pd.concat([df1, df2, df3])

# Seleccionar las columnas de interés
df = df_original[['ID', 'shotcreteThickness', 'utot_values', 'porcentajepyswarm', 'Sostenimiento', 'source']].copy()

# Filtrar solo los valores menores a 2000 en 'porcentajepyswarm'
df = df[df['porcentajepyswarm'] < 2000]
#print(df)

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

# Asegurarse de que las columnas sean numéricas, forzando conversión
df['shotcreteThickness'] = pd.to_numeric(df['shotcreteThickness'], errors='coerce')

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

# Crear un diccionario para los símbolos específicos de cada fuente
symbols_dict = {'PSO200': 'o', 'PSO400': 's', 'PSO600': 'D', 'PSO800': '^'}  # o: círculo, s: cuadrado, D: diamante, ^: triángulo

# Usar la columna 'source' para agrupar los datos y graficar
for archivo, grupo in df.groupby('source'):
    plt.scatter(
        grupo['Sostenimiento_Numerico'], 
        grupo['shotcreteThickness'], 
        color=colores_puntos[archivo], 
        label=archivo, 
        marker=symbols_dict[archivo]  # Añadir el símbolo correspondiente
    )

# Usar la columna 'source' para agrupar los datos y graficar
#for archivo, grupo in df.groupby('source'):
#    plt.scatter(grupo['Sostenimiento_Numerico'], grupo['shotcreteThickness'], color=colores_puntos[archivo], label=archivo)

# Graficar la línea recta del último valor de shotcreteThickness para cada grupo
#for archivo, grupo in df_original.groupby('source'):
    #ultimo_valor = grupo['shotcreteThickness'].iloc[-1]  # Último valor de shotcreteThickness
    #plt.axhline(y=ultimo_valor, color=line_colors[archivo], linestyle='-', linewidth=2, label=f'{archivo} solución')    
    
# Establecer las etiquetas del eje X con los nombres de sostenimiento
plt.xticks(ticks=list(mapeo_sostenimiento.values()), labels=list(mapeo_sostenimiento.keys()), rotation=45, ha='right')

# Añadir etiquetas a los ejes y título
plt.xlabel('Marcos Metálicos')
plt.ylabel('Espesor (mm)')
plt.title('')

# Mover la leyenda fuera del gráfico
plt.legend(title='Análisis PSO', loc='center left', bbox_to_anchor=(1, 0.5))

# Mostrar el gráfico
plt.grid(True)
plt.tight_layout()  # Ajusta el diseño para que las etiquetas no se corten

# Guardar la gráfica como archivo PNG
nombre_imagen = f'AnalisisPSO200400600grafica1.png'
plt.savefig(nombre_imagen, format='png', dpi=300)
print(f"Gráfico guardado como {nombre_imagen}")

plt.show()


# In[2]:


import pandas as pd
import matplotlib.pyplot as plt

# Cargar los archivos CSV
df1 = pd.read_csv('resultados_actualizados200Nvo.csv')
df2 = pd.read_csv('resultados_actualizados400Nvo.csv')
df3 = pd.read_csv('resultados_actualizados600Nvo.csv')

# Añadir una columna para identificar la fuente de cada DataFrame
df1['source'] = 'PSO200'
df2['source'] = 'PSO400'
df3['source'] = 'PSO600'

# Combinar los DataFrames
df_original = pd.concat([df1, df2, df3])

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

# Asegurarse de que las columnas sean numéricas
df['shotcreteThickness'] = pd.to_numeric(df['shotcreteThickness'], errors='coerce')
df['utot_values'] = df['utot_values'].str.strip("[]").astype(float)

# Eliminar filas con valores NaN
df = df.dropna(subset=['shotcreteThickness', 'Sostenimiento_Numerico'])

# Crear un diccionario para los símbolos específicos de cada fuente
symbols_dict = {'PSO200': 'o', 'PSO400': 's', 'PSO600': 'D'}

# Colores para los puntos
colores_puntos = {'PSO200': 'DarkOrange', 'PSO400': 'MediumSeaGreen', 'PSO600': 'RoyalBlue'}

# Crear el gráfico de dispersión 2D
plt.figure(figsize=(10, 6))

# Graficar solo los 5 valores más bajos de cada fuente con etiquetas rotadas
for source, color in colores_puntos.items():
    df_source = df[df['source'] == source]
    
    # Obtener los 5 valores mínimos de utot_values
    valores_bajos = df_source.nsmallest(5, 'utot_values')
    
    # Definir el ángulo de rotación para las etiquetas
    rotation_angle = {'PSO200': 45, 'PSO400': 45, 'PSO600': 45}[source]
    
    # Graficar los puntos
    plt.scatter(
        valores_bajos['Sostenimiento_Numerico'],
        valores_bajos['shotcreteThickness'],
        color=color,
        marker=symbols_dict[source],
        label=f'{source} (IDs: {", ".join(map(str, valores_bajos["ID"]))})'
    )
    
    # Añadir etiquetas con rotación personalizada
    for _, row in valores_bajos.iterrows():
        plt.text(
            row['Sostenimiento_Numerico'],
            row['shotcreteThickness'],
            str(row['ID']),
            fontsize=11,
            rotation=rotation_angle,
            ha='center' if source == 'PSO200' else 'right' if source == 'PSO400' else 'left',  # Aquí defines las posiciones
            #color=color
        )

# Configurar las etiquetas del eje X con los nombres de sostenimiento
plt.xticks(ticks=list(mapeo_sostenimiento.values()), labels=list(mapeo_sostenimiento.keys()), rotation=45, ha='right', fontsize=8)

# Etiquetas de los ejes
plt.xlabel('Marcos Metálicos')
plt.ylabel('Espesor (mm)')
plt.title('')

# Añadir una leyenda
plt.legend(title='Análisis PSO', loc='center left', bbox_to_anchor=(1, 0.5))

# Guardar la gráfica como archivo PNG
nombre_imagen = f'AnalisisPSO200400600grafica2.png'
plt.savefig(nombre_imagen, format='png', dpi=300)
print(f"Gráfico guardado como {nombre_imagen}")

# Mostrar el gráfico
plt.grid(True)
plt.show()


# In[3]:


import pandas as pd
import plotly.graph_objects as go

# Cargar los archivos CSV
df1 = pd.read_csv('resultados_actualizados200Nvo.csv')
df2 = pd.read_csv('resultados_actualizados400Nvo.csv')
df3 = pd.read_csv('resultados_actualizados600Nvo.csv')

# Añadir una columna para identificar la fuente de cada DataFrame
df1['source'] = 'PSO200'
df2['source'] = 'PSO400'
df3['source'] = 'PSO600'

# Combinar los DataFrames
df_resultados = pd.concat([df1, df2, df3])

# Seleccionar las columnas de interés
df = df_resultados[['ID', 'shotcreteThickness', 'utot_values', 'porcentajepyswarm', 'Sostenimiento', 'source']].copy()

# Filtro por cada fuente y eliminación de NaN
fuentes = ['PSO200', 'PSO400', 'PSO600']
dfs_filtrados = []

for fuente in fuentes:
    # Filtrar datos específicos de cada fuente y condición en porcentajepyswarm
    df_filtrado = df[(df['source'] == fuente) & (df['porcentajepyswarm'] < 2000)].copy()
    
    # Procesar columna 'Sostenimiento' y asegurar numeración
    df_filtrado['Sostenimiento'] = df_filtrado['Sostenimiento'].astype(str).str.split('x').str[1].astype(float)
    
    # Asegurarse de que las columnas sean numéricas
    df_filtrado['shotcreteThickness'] = pd.to_numeric(df_filtrado['shotcreteThickness'], errors='coerce')
    df_filtrado['utot_values'] = df_filtrado['utot_values'].apply(lambda x: float(x.strip('[]')) if isinstance(x, str) else x)
    df_filtrado['utot_values'] = pd.to_numeric(df_filtrado['utot_values'], errors='coerce')
    
    # Eliminar filas con valores NaN
    df_filtrado = df_filtrado.dropna(subset=['shotcreteThickness', 'Sostenimiento', 'utot_values'])
    dfs_filtrados.append(df_filtrado)

# Combinar nuevamente los DataFrames después del filtrado
df_final = pd.concat(dfs_filtrados)

# Crear un diccionario para los símbolos y colores
symbols_dict = {'PSO200': 'circle', 'PSO400': 'square', 'PSO600': 'diamond'}
colores_puntos = {'PSO200': 'DarkOrange', 'PSO400': 'MediumSeaGreen', 'PSO600': 'RoyalBlue'}

# Crear una figura 3D interactiva con Plotly
fig = go.Figure()

for fuente in fuentes:
    df_fuente = df_final[df_final['source'] == fuente]
    
    # Obtener los 5 IDs con los menores valores de 'utot_values' para cada fuente
    valores_bajos = df_fuente.nsmallest(5, 'utot_values')
    ids_a_marcar = valores_bajos['ID'].tolist()

    # Graficar los puntos seleccionados con los 5 menores valores de 'utot_values'
    fig.add_trace(go.Scatter3d(
        x=valores_bajos['shotcreteThickness'],
        y=valores_bajos['Sostenimiento'],
        z=valores_bajos['utot_values'],
        mode='markers+text',
        marker=dict(size=8, color=colores_puntos[fuente], symbol=symbols_dict[fuente]),
        text=valores_bajos['ID'],  # Etiqueta de ID
        textposition="top center",  # Posición de la etiqueta
        name=f'ID {fuente}: ' + ', '.join(map(str, ids_a_marcar))
    ))

# Añadir etiquetas a los ejes
fig.update_layout(
    scene=dict(
        xaxis_title='Espesor (mm)',
        yaxis_title='Marcos Metálicos',
        zaxis_title='Deformación Final'
    ),
    title="",
    legend_title="Análisis"
)

# Guardar la imagen en formato PNG
fig.write_image(f"AnalisisPSO200400600grafica3.png")


# Mostrar la figura interactiva
fig.show()


# In[4]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Lista de archivos y sus etiquetas correspondientes
archivos = [
    ('resultados_actualizados200Nvo.csv', 'PSO200', 'DarkOrange', 'o', 'circle'),
    ('resultados_actualizados400Nvo.csv', 'PSO400', 'MediumSeaGreen', 's', 'square'),
    ('resultados_actualizados600Nvo.csv', 'PSO600', 'RoyalBlue', 'D', 'RoyalBlue')
]

# Definir un diccionario para el mapeo de sostenimiento a valores numéricos
mapeo_sostenimiento = {
    '102x19.4': 0, '127x23.7': 1, '127x28.1': 2, '152x22.4': 3, '152x29.7': 4, 
    '152x37.2': 5, '203x35.9': 6, '203x41.8': 7, '203x46.2': 8, '203x52.2': 9,
    '203x59.3': 10, '203x71.4': 11, '203x86.6': 12, '203x99.8': 13, '254x49.2': 14,
    '254x58.2': 15, '254x67.4': 16, '254x72.9': 17, '254x80': 18, '254x89.1': 19,
    '254x101.3': 20, '254x114.5': 21, '254x131.2': 22, '254x148.9': 23, '254x166.6': 24,
    '305x79': 25, '305x86.1': 26, '305x96.7': 27, '305x106.9': 28, '305x117.5': 29,
    '305x129.7': 30, '305x142.8': 31, '305x158': 32, '305x178.8': 33, '305x202.1': 34,
    '305x226.4': 35, '305x253.2': 36, '305x282.6': 37, '305x313': 38, '305x342.9': 39
}

# Procesar cada archivo
for archivo, etiqueta, color_puntos, simbolo, color_linea in archivos:
    try:
        # Cargar el archivo CSV
        df = pd.read_csv(archivo)
        df['source'] = etiqueta

        # Filtrar solo los valores menores a 2000 en 'porcentajepyswarm'
        df = df[df['porcentajepyswarm'] < 2000]

        # Crear una nueva columna 'Sostenimiento_Numerico' usando el mapeo
        df['Sostenimiento_Numerico'] = df['Sostenimiento'].map(mapeo_sostenimiento)

        # Asegurarse de que las columnas sean numéricas, forzando conversión
        df['shotcreteThickness'] = pd.to_numeric(df['shotcreteThickness'], errors='coerce')

        # Eliminar filas con valores NaN
        df = df.dropna(subset=['shotcreteThickness', 'Sostenimiento_Numerico'])

        # Crear el gráfico de dispersión 2D
        plt.figure(figsize=(10, 6))
        plt.scatter(
            df['Sostenimiento_Numerico'], 
            df['shotcreteThickness'], 
            color=color_puntos, 
            label=etiqueta, 
            marker=simbolo  # Añadir el símbolo correspondiente
        )

        # Establecer las etiquetas del eje X con los nombres de sostenimiento
        plt.xticks(ticks=list(mapeo_sostenimiento.values()), labels=list(mapeo_sostenimiento.keys()), rotation=45, ha='right')

        # Añadir etiquetas a los ejes y título
        plt.xlabel('Marcos Metálicos')
        plt.ylabel('Espesor (mm)')
        plt.title(f'Análisis PSO - {etiqueta}')

        # Mover la leyenda fuera del gráfico
        plt.legend(title='Análisis PSO', loc='center left', bbox_to_anchor=(1, 0.5))

        # Mostrar el gráfico
        plt.grid(True)
        plt.tight_layout()  # Ajusta el diseño para que las etiquetas no se corten
        
        # Guardar el gráfico como archivo PNG
        nombre_imagen = f'grafico_{etiqueta}anexos1.png'
        plt.savefig(nombre_imagen, format='png', dpi=300)
        print(f"Gráfico guardado como {nombre_imagen}")
        
        # Mostrar el gráfico
        plt.show()

    except FileNotFoundError:
        print(f"El archivo {archivo} no fue encontrado. Saltando...")


# In[5]:


import pandas as pd
import matplotlib.pyplot as plt

# Lista de archivos y etiquetas correspondientes
datos = [
    ('resultados_actualizados200Nvo.csv', 'PSO200'),
    ('resultados_actualizados400Nvo.csv', 'PSO400'),
    ('resultados_actualizados600Nvo.csv', 'PSO600'),
]

# Diccionario para el mapeo de sostenimiento a valores numéricos
mapeo_sostenimiento = {
    '102x19.4': 0, '127x23.7': 1, '127x28.1': 2, '152x22.4': 3, '152x29.7': 4, '152x37.2': 5,
    '203x35.9': 6, '203x41.8': 7, '203x46.2': 8, '203x52.2': 9, '203x59.3': 10, '203x71.4': 11,
    '203x86.6': 12, '203x99.8': 13, '254x49.2': 14, '254x58.2': 15, '254x67.4': 16, '254x72.9': 17,
    '254x80': 18, '254x89.1': 19, '254x101.3': 20, '254x114.5': 21, '254x131.2': 22, '254x148.9': 23,
    '254x166.6': 24, '305x79': 25, '305x86.1': 26, '305x96.7': 27, '305x106.9': 28, '305x117.5': 29,
    '305x129.7': 30, '305x142.8': 31, '305x158': 32, '305x178.8': 33, '305x202.1': 34,
    '305x226.4': 35, '305x253.2': 36, '305x282.6': 37, '305x313': 38, '305x342.9': 39
}

# Diccionario de símbolos y colores para las gráficas
symbols_dict = {'PSO200': 'o', 'PSO400': 's', 'PSO600': 'D'}
colores_puntos = {'PSO200': 'DarkOrange', 'PSO400': 'MediumSeaGreen', 'PSO600': 'RoyalBlue'}
rotaciones = {'PSO200': 45, 'PSO400': 45, 'PSO600': 45}

# Procesar cada archivo
for archivo, etiqueta in datos:
    try:
        # Cargar el archivo CSV
        df = pd.read_csv(archivo)

        # Añadir una columna para identificar la fuente
        df['source'] = etiqueta

        # Filtrar solo las columnas necesarias
        df = df[['ID', 'shotcreteThickness', 'utot_values', 'porcentajepyswarm', 'Sostenimiento', 'source']].copy()

        # Filtrar valores menores a 2000 en 'porcentajepyswarm'
        df = df[df['porcentajepyswarm'] < 2000]

        # Mapear sostenimiento a valores numéricos
        df['Sostenimiento_Numerico'] = df['Sostenimiento'].map(mapeo_sostenimiento)

        # Convertir columnas a valores numéricos
        df['shotcreteThickness'] = pd.to_numeric(df['shotcreteThickness'], errors='coerce')
        df['utot_values'] = df['utot_values'].str.strip("[]").astype(float)

        # Eliminar filas con valores NaN
        df = df.dropna(subset=['shotcreteThickness', 'Sostenimiento_Numerico'])

        # Obtener los 5 valores más bajos de utot_values
        valores_bajos = df.nsmallest(5, 'utot_values')

        # Crear el gráfico
        plt.figure(figsize=(10, 6))
        plt.scatter(
            valores_bajos['Sostenimiento_Numerico'],
            valores_bajos['shotcreteThickness'],
            color=colores_puntos[etiqueta],
            marker=symbols_dict[etiqueta],
            label=f'{etiqueta} (IDs: {", ".join(map(str, valores_bajos["ID"]))})'
        )

        # Añadir etiquetas con rotación personalizada
        for _, row in valores_bajos.iterrows():
            plt.text(
                row['Sostenimiento_Numerico'],
                row['shotcreteThickness'],
                str(row['ID']),
                fontsize=10,
                rotation=rotaciones[etiqueta],
                ha='center' if etiqueta == 'PSO200' else 'right' if etiqueta == 'PSO400' else 'left',
            )

        # Configurar las etiquetas del eje X
        plt.xticks(
            ticks=list(mapeo_sostenimiento.values()),
            labels=list(mapeo_sostenimiento.keys()),
            rotation=45,
            ha='right',
            fontsize=8
        )

        # Etiquetas y título
        plt.xlabel('Marcos Metálicos')
        plt.ylabel('Espesor (mm)')
        plt.title(f'Gráfica {etiqueta}')
        plt.grid(True)

        # Añadir la leyenda
        plt.legend(title='Análisis PSO', loc='center left', bbox_to_anchor=(1, 0.5))

        # Ajustar el diseño
        plt.tight_layout()

        # Guardar la gráfica como archivo PNG
        nombre_imagen = f'grafico_{etiqueta}anexos2.png'
        plt.savefig(nombre_imagen, format='png', dpi=300)
        print(f"Gráfico guardado como {nombre_imagen}")

        # Mostrar el gráfico
        plt.show()

    except FileNotFoundError:
        print(f"El archivo {archivo} no fue encontrado. Saltando...")


# In[6]:


import pandas as pd
import plotly.graph_objects as go

# Lista de archivos y etiquetas de las fuentes
archivos = [
    ('resultados_actualizados200Nvo.csv', 'PSO200'),
    ('resultados_actualizados400Nvo.csv', 'PSO400'),
    ('resultados_actualizados600Nvo.csv', 'PSO600')
]

# Diccionarios de colores y símbolos
symbols_dict = {'PSO200': 'circle', 'PSO400': 'square', 'PSO600': 'diamond'}
colores_puntos = {'PSO200': 'DarkOrange', 'PSO400': 'MediumSeaGreen', 'PSO600': 'RoyalBlue'}

# Iterar sobre cada archivo y fuente para crear gráficos
for archivo, fuente in archivos:
    # Cargar el archivo CSV
    df = pd.read_csv(archivo)

    # Añadir una columna para identificar la fuente
    df['source'] = fuente

    # Seleccionar las columnas de interés
    df = df[['ID', 'shotcreteThickness', 'utot_values', 'porcentajepyswarm', 'Sostenimiento', 'source']].copy()

    # Filtrar datos específicos y eliminar valores NaN
    df = df[(df['source'] == fuente) & (df['porcentajepyswarm'] < 2000)].copy()
    df['Sostenimiento'] = df['Sostenimiento'].astype(str).str.split('x').str[1].astype(float)
    df['shotcreteThickness'] = pd.to_numeric(df['shotcreteThickness'], errors='coerce')
    df['utot_values'] = df['utot_values'].apply(lambda x: float(x.strip('[]')) if isinstance(x, str) else x)
    df = df.dropna(subset=['shotcreteThickness', 'Sostenimiento', 'utot_values'])

    # Obtener los 5 valores más bajos
    valores_bajos = df.nsmallest(5, 'utot_values')

    # Crear figura con Plotly
    fig = go.Figure()

    # Agregar los puntos
    fig.add_trace(go.Scatter3d(
        x=valores_bajos['shotcreteThickness'],
        y=valores_bajos['Sostenimiento'],
        z=valores_bajos['utot_values'],
        mode='markers+text',
        marker=dict(
            size=8,
            color=colores_puntos[fuente],  # Color específico según la fuente
            symbol=symbols_dict[fuente]   # Símbolo específico según la fuente
        ),
        text=valores_bajos['ID'],  # Etiqueta con IDs
        textposition="top center",
        name=fuente  # Nombre de la traza para la leyenda
    ))

    # Configurar la visualización
    fig.update_layout(
        scene=dict(
            xaxis_title='Espesor (mm)',
            yaxis_title='Marcos Metálicos',
            zaxis_title='Deformación Final'
        ),
        title=f"Análisis {fuente}",
        legend=dict(title="", x=0.8, y=1.0, font=dict(size=10)),
        showlegend=True
    )

    # Mostrar el gráfico
    fig.show()

    # Guardar la imagen en formato PNG
    fig.write_image(f"grafico_{fuente}anexos3.png")


# In[ ]:




