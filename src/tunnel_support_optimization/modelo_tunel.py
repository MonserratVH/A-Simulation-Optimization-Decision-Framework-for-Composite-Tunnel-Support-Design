"""
Automated PLAXIS 2D model for composite tunnel-support evaluation.

This file contains adaptations of the PLAXIS tunnel-support capacity example
originally distributed by Plaxis bv. The adapted workflow adds automated
capacity checks, PSO-oriented penalties, staged excavation, and crown-
displacement extraction. It is distributed under the Plaxis Public License;
see LICENSES/PPL-1.0.txt and docs/THIRD_PARTY_NOTICES.md.
"""
from __future__ import annotations

import math
import os
import subprocess
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PySide2.QtCore import *  # required by the original PLAXIS helper code
from easygui import msgbox
from plxscripting.easy import *

from .settings import settings

# The vendor helper expects PLAXIS-specific modules available in a licensed
# PLAXIS Python environment. Add its directory explicitly without modifying it.
_VENDOR_DIR = settings.project_root / "vendor" / "plaxis_support_capacity"
if str(_VENDOR_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(_VENDOR_DIR))
from shared_composite_tunnel_support import *  # noqa: E402,F401,F403

s_i = g_i = s_o = g_o = None
_input_process = _output_process = None


def initialize_plaxis():
    """Launch PLAXIS Input/Output and establish remote-scripting sessions."""
    global s_i, g_i, s_o, g_o, _input_process, _output_process
    settings.validate(require_geometry=True)
    input_exe = settings.plaxis_home / settings.input_executable
    output_exe = settings.plaxis_home / settings.output_executable
    if not input_exe.exists() or not output_exe.exists():
        raise FileNotFoundError(
            f"PLAXIS executables were not found under {settings.plaxis_home}"
        )
    _input_process = subprocess.Popen([
        str(input_exe),
        f"--AppServerPort={settings.input_port}",
        f"--AppServerPassWord={settings.plaxis_password}",
    ])
    _output_process = subprocess.Popen([
        str(output_exe),
        f"--AppServerPort={settings.output_port}",
        f"--AppServerPassWord={settings.plaxis_password}",
    ])
    s_i, g_i = new_server(
        "localhost", settings.input_port,
        password=settings.plaxis_password, timeout=30.0
    )
    s_o, g_o = new_server(
        "localhost", settings.output_port,
        password=settings.plaxis_password, timeout=30.0
    )
    return s_i, g_i, s_o, g_o


def close_plaxis_connections() -> None:
    """Close available remote-scripting connections without masking errors."""
    global s_i, s_o
    for server in (s_o, s_i):
        try:
            if server is not None:
                server.close()
        except Exception:
            pass


def generar_modelo_plaxis(gammaUnsat1,gammaUnsat2,gammaUnsat3,ERef1,ERef2,\
                          Erm,nu1,nu2,nu3,cRef1,cRef2,phi1,phi2,AbsSigmaCI, mi, GSI, Disturbance,\
                          w, EA1, EI, StructNu):
    
    #Crea una hoja nueva
    s_i.new()
 
    #Importamos el contorno del suelo
    print(g_i.import_(str(settings.topography_dxf), "ImportType",\
    "structures", "ImportFilter", "points|lines|polygons", "ScalingVector", (1, 1), "Offset", (0, 0)))

    #Genera las propiedades del material
    Unidad1= g_i.soilmat("Identification", "Unidad1", "SoilModel", "hoekbrown", "DrainageType",\
                "Non-porous", "gammaUnsat", gammaUnsat3, "Erm", Erm, "nu", nu3,\
                "AbsSigmaCI", AbsSigmaCI, "mi", mi, "GSI", GSI, "Disturbance", Disturbance)
    Unidad2= g_i.soilmat("Identification", "Unidad2", "SoilModel", "hoekbrown", "DrainageType",\
                "Non-porous", "gammaUnsat", gammaUnsat3, "Erm", Erm, "nu", nu3,\
                "AbsSigmaCI", AbsSigmaCI, "mi", mi, "GSI", GSI, "Disturbance", Disturbance)
    Unidad3= g_i.soilmat("Identification", "Unidad3", "SoilModel", "hoekbrown", "DrainageType",\
                "Non-porous", "gammaUnsat", gammaUnsat3, "Erm", Erm, "nu", nu3,\
                "AbsSigmaCI", AbsSigmaCI, "mi", mi, "GSI", GSI, "Disturbance", Disturbance)

    #Asigna los materiales a la capas de suelo actualmente configuradas
    g_i.gotostructures()
    g_i.Polygon_3.Soil.Material = Unidad1
    g_i.Polygon_2.Soil.Material = Unidad2
    g_i.Polygon_1.Soil.Material = Unidad3

    #Ubica el tunel en las coordenadas predichas
    tunnel = g_i.tunnel(89.4777,53.1668)  #X=99.0973 Y=67.8026
    g_i.importcrosssection(tunnel, str(settings.tunnel_section_dxf),\
                           "Scale", 1, "Tolerance", 0.0001, "Segments", (0,1,2,3,4), "Subsections",\
                           (0,1,2,3,4,5,6,7,8), "SegmentsOrigin", (1, "EndPoint"), "Intersect", True)

    #Define el revestimiento
    g_i.platemat("Identification", "Lining", "MaterialType", "Elastic", "w", w,\
                 "EA1", EA1, "EI", EI, "StructNu", StructNu)

    # define las lineas, asigna el revestimiento, crea la interfaz negativa
    for tunnel_slice in tunnel.SliceSegments[:]:
        g_i.plate(tunnel_slice)
        tunnel_slice.Plate.Material = g_i.Lining
        g_i.neginterface(tunnel_slice)

    #Genera el túnel
    g_i.generatetunnel(tunnel)
    
    #Genera los desplazamientos laterales
    point1_g = g_i.point(0.00, 124.6)
    point2_g = g_i.point(0.00, 0.00)
    point3_g = g_i.point(200.00, 0.00)
    point4_g = g_i.point(200.00, 94.76)
    linedisplacement1_g = g_i.linedispl(point1_g, point2_g, "Displacement_x", "Fixed", "Displacement_y", "Free")
    linedisplacement2_g = g_i.linedispl(point2_g, point3_g, "Displacement_x", "Fixed", "Displacement_y", "Fixed")
    linedisplacement3_g = g_i.linedispl(point3_g, point4_g, "Displacement_x", "Fixed", "Displacement_y", "Free")
    

    #Genera el mallado
    g_i.gotomesh()

    #Genera un refinamiento a la malla en la zona del tunel
    g_i.Polycurve_1_1.CoarsenessFactor=0.15
    g_i.Polycurve_2_1.CoarsenessFactor=0.15
    g_i.Polycurve_3_1.CoarsenessFactor=0.15
    g_i.Polycurve_7_1.CoarsenessFactor=0.15
    g_i.Polycurve_10_1.CoarsenessFactor=0.15
    g_i.Polycurve_13_1.CoarsenessFactor=0.15
    g_i.Polycurve_12_1.CoarsenessFactor=0.15
    g_i.Polycurve_11_1.CoarsenessFactor=0.15
    g_i.Polycurve_7_1.CoarsenessFactor=0.15


    #Define el proporcionamiento de la malla
    g_i.mesh(0.04)

    #Genera un refinamiento a la malla en la zona del tunel
    g_i.refine(tunnel)

    #Genera las etapas de excavación
    g_i.gotostages()

    #Etapa de Fase Inicial
    phase0_s = g_i.InitialPhase
    g_i.Polygon_3_1.activate(phase0_s)
    g_i.Polygon_2_1.activate(phase0_s)
    g_i.Polygon_1_5.activate(phase0_s)
    g_i.Polygon_1_1.activate(phase0_s)
    g_i.Polygon_1_2.activate(phase0_s)
    g_i.Polygon_1_3.activate(phase0_s)
    g_i.Polygon_1_4.activate(phase0_s)
    
    #Se cambia los parametros de la FASE Inicial
    g_i.InitialPhase.DeformCalcType = "Gravity loading"
    
    #Activar las lineas de desplazamiento
    g_i.Line_1_1.activate(phase0_s)
    g_i.Line_1_2.activate(phase0_s)
    g_i.Line_1_3.activate(phase0_s)
    g_i.Line_2_1.activate(phase0_s)
    g_i.Line_2_2.activate(phase0_s)
    g_i.Line_3_4.activate(phase0_s)
    g_i.Line_3_3.activate(phase0_s)
    g_i.Line_3_2.activate(phase0_s)
    
    #Genera las etapas de excavación (Etapa 1)
    g_i.gotostages()

    #Etapa de Parte Superior
    phase1_s = g_i.phase(phase0_s)

    #Se cambia los parametros de la FASE 1
    g_i.Phase_1.Deform.Loading.SumMstage=1.0
    g_i.Phase_1.Deform.UseDefaultIterationParams = False
    g_i.Phase_1.MaxStepsStored = 256
    g_i.Phase_1.Deform.MaxLoadFractionPerStep = 0.025
    
    #Desactivar la zona de excavacion
    g_i.setcurrentphase(phase1_s)
    g_i.Polygon_1_1.deactivate(phase1_s)
    
    
    #Se activa la Fase Negativa
    g_i.NegativeInterface_1_1.activate(phase1_s)
    g_i.NegativeInterface_2_1.activate(phase1_s)
    g_i.NegativeInterface_3_1.activate(phase1_s)
    g_i.NegativeInterface_6_1.activate(phase1_s)
    g_i.NegativeInterface_5_1.activate(phase1_s)
    g_i.NegativeInterface_4_1.activate(phase1_s)
    
    
    #Etapa de Banqueo Zona Central
    phase2_s = g_i.phase(phase1_s)
    #Desactivar la zona de excavacion
    g_i.setcurrentphase(phase2_s)
    g_i.Polygon_1_2.deactivate(phase2_s)
    
    #Se desactiva y activa la Fase Negativa
    g_i.NegativeInterface_5_1.deactivate(phase2_s)
    g_i.NegativeInterface_8_1.activate(phase2_s)
    g_i.NegativeInterface_9_1.activate(phase2_s)
    g_i.NegativeInterface_12_1.activate(phase2_s)

    #Etapa de Banqueo Zona Central
    phase3_s = g_i.phase(phase2_s)
    #Desactivar la zona de excavacion
    g_i.setcurrentphase(phase3_s)
    g_i.Polygon_1_3.deactivate(phase3_s)
    g_i.Polygon_1_4.deactivate(phase3_s)
    
    #Se desactiva y activa la Fase Negativa
    g_i.NegativeInterface_4_1.deactivate(phase3_s)
    g_i.NegativeInterface_6_1.deactivate(phase3_s)
    g_i.NegativeInterface_9_1.deactivate(phase3_s)
    g_i.NegativeInterface_8_1.deactivate(phase3_s)
    g_i.NegativeInterface_10_1.activate(phase3_s)
    g_i.NegativeInterface_13_1.activate(phase3_s)
    g_i.NegativeInterface_11_1.activate(phase3_s)
    g_i.NegativeInterface_7_1.activate(phase3_s)


    # Selecciona los puntos de la malla
    output_port = g_i.selectmeshpoints()

    # Añade los nodos
    g_o.addcurvepoint("node", 99.61, 69.99)
    g_o.update()

    #Calcular el modelo
    g_i.calculate()

    ##Inicia la etapa de calculos
    #Abrir el Visor de Outpot de Plaxis
    g_i.gotostages()
    phase3_s = g_i.Phases[-1]
    g_i.view(phase3_s)

    # Seleccionar la fase del modelo de PLAXIS 2D
    phase = g_o.Phase_3

    # Seleccionar los tipos de resultado
    X = g_o.ResultTypes.Soil.X
    Y = g_o.ResultTypes.Soil.Y
    stresspointID = g_o.ResultTypes.Soil.StressPointID
    resulttype = g_o.ResultTypes.Soil.PlasticPoint

    # Seleccionar nodal o stress point data
    source = "stresspoint"

    # Obtener los resultados de PlasticPoint, X, Y, y stresspointID
    X_results = g_o.getresults(phase, X, source)
    Y_results = g_o.getresults(phase, Y, source)
    stresspointID_results = g_o.getresults(phase, stresspointID, source)
    PlasticPoint_results = g_o.getresults(phase, resulttype, source)
    
    #Centro del tunel
    #Centro de la Seccion31+160 X=100.0274    TunelX=10.5501     Centro de la Seccion30+880 X=99.0975
    #Centro de la Seccion31+160 Y=57.9955     TunelY=5.0260      Centro de la Seccion30+880 Y=72.6312

    # Coordenadas del centro del túnel
    center_x = 100.0274
    center_y = 57.9955

    # Calcular las coordenadas de los puntos plásticos
    x_coords = []
    y_coords = []
    for i in range(len(PlasticPoint_results)):
        if PlasticPoint_results[i] != 0:
            x_coords.append(X_results[i])
            y_coords.append(Y_results[i])

    # Calcular la distancia perpendicular más alejada del centro del túnel 
    max_distance = 0
    for x, y in zip(x_coords, y_coords):
        distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        if distance > max_distance:
            max_distance = distance

    # Graficar los puntos
    #plt.scatter(x_coords, y_coords, color='blue', label='Puntos plásticos')
    #plt.scatter(center_x, center_y, color='red', label='Centro', marker='X', s=100)
    # Calcular los límites de la gráfica
    #x_min = min(x_coords) - 1  # Restamos 1 para dejar un pequeño margen
    #x_max = max(x_coords) + 1  # Sumamos 1 para dejar un pequeño margen
    #y_min = min(y_coords) - 1  # Restamos 1 para dejar un pequeño margen
    #y_max = max(y_coords) + 1  # Sumamos 1 para dejar un pequeño margen
    # Establecer los límites de la gráfica
    #plt.xlim(x_min, x_max)
    #plt.ylim(y_min, y_max)
    # Agregar etiquetas y título al gráfico
    #plt.xlabel('Coordenada X')
    #plt.ylabel('Coordenada Y')
    #plt.title('Gráfico de Coordenadas de Puntos Plásticos')
    # Mostrar leyenda
    #plt.legend()
    # Mostrar el gráfico
    #plt.show()

    # El radio plástico es la distancia perpendicular más alejada
    plastic_radius = max_distance

    # Datos iniciales para las listas
    utot = []
    sum_mstage = []
    phaseorder = [g_o.Phase_1]

    # Obtener los resultados de deformaciones y etapas
    # Iterar sobre cada fase y cada paso dentro de esa fase
    for phase in phaseorder:
        for step in phase.Steps.value:
            utot.append(g_o.getcurveresults(g_o.Nodes[0], step, g_o.ResultTypes.Soil.Utot))
            sum_mstage.append(step.Reached.SumMstage.value)

    # Graficar los resultados
    #plt.figure(figsize=(10, 6))
    # Graficar utot en función de sum_mstage
    #plt.plot(sum_mstage, utot, marker='o', linestyle='-', color='b', label='Utot vs. SumMstage')
    #plt.title('Deformaciones Utot vs. Etapas SumMstage')
    #plt.xlabel('SumMstage')
    #plt.ylabel('Utot')
    #plt.legend()
    #plt.grid()
    #plt.show()

    # Obtener el valor máximo de utot 
    max_utot = max(utot)

    #Realiza la grafica de 'N. Vlachopoulos y M. S. Diederichs' para la obtencion del LDP
    # Definir los parámetros
    A = 197.07 # El area de la seccion del túnel
    D = math.sqrt((4*A)/math.pi) #Del paper A TWO-DIMENSIONAL APPROACH FOR DESIGNING TUNNEL SUPPORT IN WEAK ROCK
    Rt= D/2
    max_distance =  23.745    # Supongamos que el radio máximo del túnel es 7.915 y se aplica que no sea mayor de 3 veces
    x=2.0 #Distancia de la cara del túnel en m
    # Comprobamos si el radio plástico calculado supera el radio máximo del túnel
    if plastic_radius > max_distance:
        Rp = max_distance
    else:
        Rp = plastic_radius
    EjeX= x/Rt 
    R = Rp/Rt
    umax = max_utot #Obtenido de la grafica 'Deformaciones vs. Etapas'
    u0 = 1 / 3 * (np.exp(-0.15 * R**2)) * umax
    u0x = u0 / umax
    x1 = np.linspace(-5, 0, 100)
    x2 = np.linspace(0, 12, 100)
    # Definir el rango de x
    x11 = np.linspace(-5, 0, 100)
    x12 = np.linspace(0, 12, 100)
    # Calcular y graficar las curvas de ajuste
    y6 = u0x * (np.exp(x1))
    y7 = 1 - (1 - u0x) * np.exp(-(3 * x2) / (2 * R))
    # Graficar las curvas de ajuste
    #plt.plot(x1, y6, label='y6')
    #plt.plot(x2, y7, label='y7')
    # Agregar etiquetas y título al gráfico
    #plt.xlabel('Eje X')
    #plt.ylabel('Eje Y')
    #plt.title('Curvas de ajuste para N. Vlachopoulos y M. S. Diederichs')
    # Mostrar leyenda
    #plt.legend()
    # Mostrar el gráfico
    #plt.show()

    # Seleccionar un punto en la curva
    x_punto = EjeX
    y_punto = np.interp(x_punto, x12, y7)
    Utarget= y_punto*umax

    # Seleccionar un punto en la curva de la grafica "Deformaciones vs. Etapas"
    y_point = Utarget
    x_point = np.interp(y_point, utot, sum_mstage)
    #print(x_point)

    return phase0_s, x_point
    
def generar_sostenimiento(phase0_s, x_point,shotcreteCompressiveStrength, shotcretePoissonRatio,\
                              shotcreteTensileStrength, shotcreteThickness, shotcreteUnitWeight,\
                              shotcreteYoungModulus, steelSetArea, steelSetCompressiveStrength,\
                              steelSetInertia, steelSetPoissonRatio, steelSetSectionDepth, steelSetSpacing,\
                              steelSetTensileStrength,steelSetYoungModulus,steelUnitWeight,utot_values,\
                          utot_values2, w, EA1, EI, StructNu):
    
    # Inicializa utot y utot2 dentro de la función
    utot = []  # Lista para almacenar los valores de utot
    utot2 = []  # Lista para almacenar los valores de utot al inicio
    
    #Genera las etapas de excavación (Etapa 2)
    g_i.gotostages()

    #Etapa de Relajacion del Túnel
    phase4_s = g_i.phase(phase0_s)
    g_i.setcurrentphase(phase4_s)

    #Se cambia los parametros de la FASE 2
    if float(x_point) < 0.001:
        g_i.Phase_4.Deform.Loading.SumMstage = 0.001
    else:
        g_i.Phase_4.Deform.Loading.SumMstage = x_point
    g_i.Phase_4.Deform.UseDefaultIterationParams = True
    
    g_i.Lining.w = w
    g_i.Lining.EA1 = EA1
    g_i.Lining.EI = EI
    g_i.Lining.StructNu = StructNu

    #Etapa de Instalacion del Soporte Parte Superior
    phase5_s = g_i.phase(phase4_s)
    g_i.setcurrentphase(phase5_s)

    #Se cambia los parametros de la FASE 3
    g_i.Phase_5.Deform.Loading.SumMstage = 1.00
    g_i.Phase_5.Deform.SumMweight = 1.00
    g_i.Polygon_1_1.deactivate(phase5_s)

    #Se activa el Plate (Revestimiento) y la Fase Negativa
    g_i.Plate_1_1.activate(phase5_s)
    g_i.Plate_2_1.activate(phase5_s)
    g_i.Plate_3_1.activate(phase5_s)

    g_i.NegativeInterface_1_1.activate(phase5_s)
    g_i.NegativeInterface_2_1.activate(phase5_s)
    g_i.NegativeInterface_3_1.activate(phase5_s)
    g_i.NegativeInterface_6_1.activate(phase5_s)
    g_i.NegativeInterface_5_1.activate(phase5_s)
    g_i.NegativeInterface_4_1.activate(phase5_s)
    
    #Etapa de Instalacion del Soporte
    phase6_s = g_i.phase(phase5_s)
    g_i.setcurrentphase(phase6_s)
    
    #Se cambia los parametros de la FASE 3
    g_i.Polygon_1_2.deactivate(phase6_s)
    
    #Se desactiva y activa la Fase Negativa
    g_i.NegativeInterface_5_1.deactivate(phase6_s)
    g_i.NegativeInterface_8_1.activate(phase6_s)
    g_i.NegativeInterface_9_1.activate(phase6_s)
    g_i.NegativeInterface_12_1.activate(phase6_s)

    
    #Etapa de Instalacion del Soporte
    phase7_s = g_i.phase(phase6_s)
    g_i.setcurrentphase(phase7_s)
    
    #Se cambia los parametros de la FASE 3
    g_i.Polygon_1_3.deactivate(phase7_s)
    g_i.Polygon_1_4.deactivate(phase7_s)
    
    #Se activa el Plate (Revestimiento)
    g_i.Plate_7_1.activate(phase7_s)
    g_i.Plate_10_1.activate(phase7_s)
    
    #Se desactiva y activa la Fase Negativa
    g_i.NegativeInterface_4_1.deactivate(phase7_s)
    g_i.NegativeInterface_6_1.deactivate(phase7_s)
    g_i.NegativeInterface_9_1.deactivate(phase7_s)
    g_i.NegativeInterface_8_1.deactivate(phase7_s)
    g_i.NegativeInterface_10_1.activate(phase7_s)
    g_i.NegativeInterface_13_1.activate(phase7_s)
    g_i.NegativeInterface_11_1.activate(phase7_s)
    g_i.NegativeInterface_7_1.activate(phase7_s)

    
    #Calcular el modelo
    g_i.calculate()
    
    #Abrir el Visor de Outpot de Plaxis
    g_i.gotostages()
    phase7_s = g_i.Phases[-1]
    g_i.view(phase7_s)
    
    ############## Codigo para las envolventes
    selected_phase = (phase7_s) # Se selecciona la fase de la cual queremos obtener los resultados
    section_name = "Lining" # Se selecciona el sostenimiento que se empleo
    #Se selecciona el archivo donde se alamcena la informacion de las propiedades del sostenimiento
    path = {"Lining": {
            "shotcreteCompressiveStrength": shotcreteCompressiveStrength,
            "shotcretePoissonRatio": shotcretePoissonRatio,
            "shotcreteTensileStrength": shotcreteTensileStrength,
            "shotcreteThickness": shotcreteThickness,
            "shotcreteUnitWeight": shotcreteUnitWeight,
            "shotcreteYoungModulus": shotcreteYoungModulus,
            "steelSetArea": steelSetArea,
            "steelSetCompressiveStrength": steelSetCompressiveStrength,
            "steelSetInertia": steelSetInertia,
            "steelSetPoissonRatio": steelSetPoissonRatio,
            "steelSetSectionDepth": steelSetSectionDepth,
            "steelSetSpacing": steelSetSpacing,
            "steelSetTensileStrength": steelSetTensileStrength,
            "steelSetYoungModulus": steelSetYoungModulus,
            "steelUnitWeight": steelUnitWeight
        }
            }
    envelope_type = "Carranza-Torres & Diederichs" # Se selecciona el tipo de envolvente para este caso se selecciona "Carranza-Torres & Diederichs 
    fos = [1.5] # Se seleccionan los valores de los factores de seguridad
    #
    #
    #
    def check_platemat_existence(plate_mat_name):
        has_material = False
        for material in g_o.Materials:
            if material.TypeName.value == 'PlateMat' and material.Identification.value == plate_mat_name:
                has_material = True
        return has_material

    def get_moment_thrust_shear(section_name, phase):

        results_moment = []
        results_thrust = []
        results_shear = []
        has_failed = False

        ##########
        mx_all = []
        my_all = []

        # Crear una gráfica de dispersión fuera del bucle
        fig, ax = plt.subplots()
        ##########

        for plateCluster in g_o.Plates:
            for plate in plateCluster:
                if plate.Material.Identification == section_name:
                    try:
                        m = g_o.getresults(plate, phase, g_o.ResultTypes.Plate.M2D, "node")
                    except :
                    #except Exception as e:
                    #    error_message = f"Could not get moment results for plate {section_name} " \
                    #                    f"in phase {phase.Identification.value}\n[{e}]"
                    #    show_error_dialog(error_message)
                        has_failed = True
                        break    
                    results_moment = results_moment + [x for x in m]

                    try:
                        n = g_o.getresults(plate, phase, g_o.ResultTypes.Plate.Nx2D, "node")
                    except :
                    #except Exception as e:
                    #    error_message = f"Could not get normal force results for plate {section_name} " \
                    #                    f"in phase {phase.Identification.value}\n[{e}]"
                    #    show_error_dialog(error_message)
                        has_failed = True
                        break
                    results_thrust = results_thrust + [x for x in n]

                    try:
                        s = g_o.getresults(plate, phase, g_o.ResultTypes.Plate.Q2D, "node")
                    except :
                    #except Exception:
                    #    error_message = "Could not get shear force results for plate \"" \
                    #                    + section_name +\
                    #                    "\" in phase "\
                    #                    + phase.Identification.value
                    #    show_error_dialog(error_message)
                        has_failed = True
                        break
                    results_shear = results_shear + [x for x in s]
                    
                    #########
                    # Obtener las coordenadas en la dirección X
                    mx = g_o.getresults(plate, phase, g_o.ResultTypes.Plate.X, 'node')
                    mx_all.extend(mx)
    
                    # Obtener las coordenadas en la dirección Y
                    my = g_o.getresults(plate, phase, g_o.ResultTypes.Plate.Y, 'node')
                    my_all.extend(my)                    

       # Agregar todos los puntos al mismo gráfico
        ax.scatter(mx_all, my_all)

        # Configurar la gráfica
        ax.set_xlabel('Coordenada X')
        ax.set_ylabel('Coordenada Y')
        ax.set_title('Grafico de Coordenadas de Nodos')

        # Mostrar la gráfica
        plt.show()

        return has_failed, results_moment, results_thrust, results_shear                                  
        ########

    def redistribute(m_tot, n_tot, q_tot, prop):

        spacing = prop['steelSetSpacing']
        n = 1.0 / spacing

        young_st = prop['steelSetYoungModulus']
        v_st = prop['steelSetPoissonRatio']
        young_sh = prop['shotcreteYoungModulus']
        v_sh = prop['shotcretePoissonRatio']
        area_st = prop['steelSetArea']
        inertia_st = prop['steelSetInertia']
        t_sh = prop['shotcreteThickness']

        d_st = n * (young_st * area_st) / (1 - v_st**2)
        k_st = n * (young_st * inertia_st) / (1 - v_st**2)
        d_sh = (young_sh * t_sh) / (1 - v_sh**2)
        k_sh = (young_sh * t_sh**3) / (12. * (1 - v_sh**2))
        #
        m_st = [x * spacing * k_st / (k_st + k_sh) for x in m_tot]  # multiply by spacing to get result per set
        m_sh = [x * k_sh / (k_st + k_sh) for x in m_tot]
        n_st = [x * spacing * d_st / (d_st + d_sh) for x in n_tot]  # multiply by spacing to get result per set
        n_sh = [x * d_sh / (d_st + d_sh) for x in n_tot]
        q_st = [x * spacing * k_st / (k_st + k_sh) for x in q_tot]  # multiply by spacing to get result per set
        q_sh = [x * k_sh / (k_st + k_sh) for x in q_tot]
        #
        results = {
            'steel':
            {
                'm': m_st,
                'n': n_st,
                'q': q_st
            },
            'shotcrete':
            {
                'm': m_sh,
                'n': n_sh,
                'q': q_sh
            }
        }
        #
        return results


    def moment_thrust_capacity(sig_tens, sig_comp, area, inertia, t, env_type, fos):

        envelopes_comp = []
        envelopes_tens = []
        if env_type == "Carranza-Torres & Diederichs":
            n_max = [area*sig_tens/fs for fs in fos]
            n_min = [area*sig_comp/fs for fs in fos]
            m_max = [(sig_tens-sig_comp)*inertia/t/fs for fs in fos]
            m_min = [-(sig_tens-sig_comp)*inertia/t/fs for fs in fos]
            n_cr = [area*(sig_tens+sig_comp)/2/fs for fs in fos]
            for i in range(len(fos)):
                m = [m_min[i], 0, m_max[i]]
                n_comp = [n_cr[i], n_min[i], n_cr[i]]
                n_tens = [n_cr[i], n_max[i], n_cr[i]]
                envelopes_comp.append((m, n_comp))
                envelopes_tens.append((m, n_tens))
        else:
            print("Method not implemented")
        return envelopes_comp, envelopes_tens


    def shear_force_thrust_capacity(sig_tens, sig_comp, area, env_type, fos):

        envelopes_comp = []
        envelopes_tens = []
        if env_type == "Carranza-Torres & Diederichs":
            q_cr = [area/fs*(-4*sig_tens*sig_comp/9)**0.5 for fs in fos]
            i = 0
            for fs in fos:
                q = np.linspace(-q_cr[i], q_cr[i], 50)
                n_comp = sig_comp*area/fs-9*q**2*fs/(4*sig_comp*area)
                n_tens = sig_tens*area/fs-9*q**2*fs/(4*sig_tens*area)
                envelopes_comp.append((q, n_comp))
                envelopes_tens.append((q, n_tens))
                i = i + 1
        else:
            print("Method not implemented")
        return envelopes_comp, envelopes_tens


    def envelops(section_prop, envelope_type, fos):

        sig_tens_steel = section_prop['steelSetTensileStrength']
        sig_comp_steel = - section_prop['steelSetCompressiveStrength']
        area_steel = section_prop['steelSetArea']
        inertia_steel = section_prop['steelSetInertia']
        thickness_steel = section_prop['steelSetSectionDepth']
        #
        sig_tens_shotcrete = section_prop['shotcreteTensileStrength']
        sig_comp_shotcrete = - section_prop['shotcreteCompressiveStrength']
        area_shotcrete = section_prop['shotcreteThickness']
        inertia_shotcrete = section_prop['shotcreteThickness'] ** 3 / 12.
        thickness_shotcrete = section_prop['shotcreteThickness']
        #
        m_n_steel_comp_envelops, m_n_steel_tens_envelops = moment_thrust_capacity(
            sig_tens_steel, sig_comp_steel, area_steel, inertia_steel, thickness_steel, envelope_type, fos)
        #
        m_n_shotcrete_comp_envelops, m_n_shotcrete_tens_envelops = moment_thrust_capacity(
            sig_tens_shotcrete, sig_comp_shotcrete, area_shotcrete, inertia_shotcrete, thickness_shotcrete, envelope_type,
            fos)
        #
        q_n_steel_comp_envelops, q_n_steel_tens_envelops = shear_force_thrust_capacity(
            sig_tens_steel, sig_comp_steel, area_steel, envelope_type, fos)
        #
        q_n_shotcrete_comp_envelops, q_n_shotcrete_tens_envelops = shear_force_thrust_capacity(
            sig_tens_shotcrete, sig_comp_shotcrete, area_shotcrete, envelope_type, fos)
        #
        envelopes = {
            'steel':
            {
                'mn':
                {
                    'comp': m_n_steel_comp_envelops,
                    'tens': m_n_steel_tens_envelops
                },
                'qn':
                {
                    'comp': q_n_steel_comp_envelops,
                    'tens': q_n_steel_tens_envelops
                }
            },
            'shotcrete':
            {
                'mn':
                {
                    'comp': m_n_shotcrete_comp_envelops,
                    'tens': m_n_shotcrete_tens_envelops
                },
                'qn':
                {
                    'comp': q_n_shotcrete_comp_envelops,
                    'tens': q_n_shotcrete_tens_envelops
                }
            }
        }
        return envelopes


    def display_results(results, envelopes, fos):

        # Retrieve what needs to be displayed from dictionaries
        #
        # Component results
        moment_steel = results['steel']['m']
        thrust_steel = results['steel']['n']
        shear_steel = results['steel']['q']
        moment_shotcrete = results['shotcrete']['m']
        thrust_shotcrete = results['shotcrete']['n']
        shear_shotcrete = results['shotcrete']['q']
        #
        # Envelopes
        moment_thrust_steel_compression_envelopes = envelopes['steel']['mn']['comp']
        moment_thrust_steel_tension_envelopes = envelopes['steel']['mn']['tens']
        moment_thrust_shotcrete_compression_envelopes = envelopes['shotcrete']['mn']['comp']
        moment_thrust_shotcrete_tension_envelopes = envelopes['shotcrete']['mn']['tens']
        shear_force_thrust_steel_compression_envelopes = envelopes['steel']['qn']['comp']
        shear_force_thrust_steel_tension_envelopes = envelopes['steel']['qn']['tens']
        shear_force_thrust_shotcrete_compression_envelopes = envelopes['shotcrete']['qn']['comp']
        shear_force_thrust_shotcrete_tension_envelopes = envelopes['shotcrete']['qn']['tens']
        
        #print(f"moment_thrust_steel_compression_envelopes: {moment_thrust_steel_compression_envelopes}")
        #print(f"moment_thrust_steel_tension_envelopes: {moment_thrust_steel_tension_envelopes}")
        #print(f"moment_thrust_shotcrete_compression_envelopes: {moment_thrust_shotcrete_compression_envelopes}")
        #print(f"moment_thrust_shotcrete_tension_envelopes: {moment_thrust_shotcrete_tension_envelopes}")
        #print(f"shear_force_thrust_steel_compression_envelopes: {shear_force_thrust_steel_compression_envelopes}")
        #print(f"shear_force_thrust_steel_tension_envelopes: {shear_force_thrust_steel_tension_envelopes}")
        #print(f"shear_force_thrust_shotcrete_compression_envelopes: {shear_force_thrust_shotcrete_compression_envelopes}")
        #print(f"shear_force_thrust_shotcrete_tension_envelopes: {shear_force_thrust_shotcrete_tension_envelopes}")
        
        # Display results
        fig, ((axNMSteel, axNMShotcrete), (axQNSteel, axQNShotcrete)) = plt.subplots(nrows=2, ncols=2)
        #
        fos_color = ["lightsalmon", "orangered", "red", "darkred"]
        n_fos_color = len(fos_color)
        fos_label = ["FoS=" + str(fs) for fs in fos]
        #
        axNMSteel.set_title('Steel reinforcement')
        axNMSteel.set_xlabel("Moment M (" + unitForce + "." + unitLength + ")")
        axNMSteel.set_ylabel("Thrust N (" + unitForce + ")")
        axNMSteel.scatter(moment_steel, thrust_steel)
        for i in range(len(fos)):
            axNMSteel.plot(
                moment_thrust_steel_compression_envelopes[i][0],
                moment_thrust_steel_compression_envelopes[i][1],
                color=fos_color[i % n_fos_color], label=fos_label[i])
            axNMSteel.plot(
                moment_thrust_steel_tension_envelopes[i][0],
                moment_thrust_steel_tension_envelopes[i][1],
                color=fos_color[i % n_fos_color])
        #
        axNMShotcrete.set_title('Shotcrete')
        axNMShotcrete.set_xlabel("Moment M (" + unitForce + "." + unitLength + "/" + unitLength + ")")
        axNMShotcrete.set_ylabel("Thrust N (" + unitForce + "/" + unitLength + ")")
        axNMShotcrete.scatter(moment_shotcrete, thrust_shotcrete)
        for i in range(len(fos)):
            axNMShotcrete.plot(
                moment_thrust_shotcrete_compression_envelopes[i][0],
                moment_thrust_shotcrete_compression_envelopes[i][1],
                color=fos_color[i % n_fos_color])
            axNMShotcrete.plot(
                moment_thrust_shotcrete_tension_envelopes[i][0],
                moment_thrust_shotcrete_tension_envelopes[i][1],
                color=fos_color[i % n_fos_color])
        #
        #
        axQNSteel.set_title('Steel reinforcement')
        axQNSteel.set_xlabel("Shear Q (" + unitForce + ")")
        axQNSteel.set_ylabel("Thrust N (" + unitForce + ")")
        axQNSteel.scatter(shear_steel, thrust_steel)
        for i in range(len(fos)):
            axQNSteel.plot(
                shear_force_thrust_steel_compression_envelopes[i][0],
                shear_force_thrust_steel_compression_envelopes[i][1],
                color=fos_color[i % n_fos_color])
            axQNSteel.plot(
                shear_force_thrust_steel_tension_envelopes[i][0],
                shear_force_thrust_steel_tension_envelopes[i][1],
                color=fos_color[i % n_fos_color])
        #
        axQNShotcrete.set_title('Shotcrete')
        axQNShotcrete.set_xlabel("Shear Q  (" + unitForce + "/" + unitLength + ")")
        axQNShotcrete.set_ylabel("Thrust N (" + unitForce + "/" + unitLength + ")")
        axQNShotcrete.scatter(shear_shotcrete, thrust_shotcrete)
        for i in range(len(fos)):
            axQNShotcrete.plot(
                shear_force_thrust_shotcrete_compression_envelopes[i][0],
                shear_force_thrust_shotcrete_compression_envelopes[i][1],
                color=fos_color[i % n_fos_color])
            axQNShotcrete.plot(
                shear_force_thrust_shotcrete_tension_envelopes[i][0],
                shear_force_thrust_shotcrete_tension_envelopes[i][1],
                color=fos_color[i % n_fos_color])
        #
        fig.legend(
                   loc="lower center",  # Position of legend
                   ncol=len(fos_label),
                   borderaxespad=0.1,  # Small spacing around legend box
                   )
        #set_program_toolbar_icon(plt.get_current_fig_manager().window)
        plt.get_current_fig_manager().set_window_title('Support Capacity Plot')
        plt.show()
        
    class SupportCapacityPlotDB(QDialog):

        def __init__(self, composite_sections, parent=None):
            super(SupportCapacityPlotDB, self).__init__(parent)
            self.compositeSections = composite_sections
            #
            self.setObjectName("SupportCapacityPlotDB")
            self.resize(380, 395)
            #
            main_layout = QVBoxLayout()
            self.setLayout(main_layout)
            #
            self.supportElementLabel = QLabel(self)
            self.supportElementLabel.setObjectName("supportElementLabel")
            self.supportElementComboBox = QComboBox(self)
            self.supportElementComboBox.setObjectName("supportElementComboBox")
            #
            support_form_layout = QFormLayout(self)
            main_layout.addLayout(support_form_layout)
            support_form_layout.addRow(self.supportElementLabel)
            support_form_layout.addRow(self.supportElementComboBox)
            #
            self.envelopeTypeComboBox = QComboBox(self)
            self.envelopeTypeComboBox.setObjectName("envelopeTypeComboBox")
            self.envelopeTypeLabel = QLabel(self)
            self.envelopeTypeLabel.setObjectName("envelopeTypeLabel")
            #
            envelope_form_layout = QFormLayout(self)
            main_layout.addLayout(envelope_form_layout)
            envelope_form_layout.addRow(self.envelopeTypeLabel)
            envelope_form_layout.addRow(self.envelopeTypeComboBox)
            #
            self.factorOfSafetyGroupBox = QGroupBox(self)
            self.factorOfSafetyGroupBox.setObjectName("factorOfSafetyGroupBox")
            #
            group_box_fos_form_layout = QFormLayout(self)
            self.factorOfSafetyGroupBox.setLayout(group_box_fos_form_layout)
            main_layout.addLayout(group_box_fos_form_layout)
            main_layout.addWidget(self.factorOfSafetyGroupBox, 1)

            self.numberOfEnvelopsLabel = QLabel(self.factorOfSafetyGroupBox)
            self.numberOfEnvelopsLabel.setObjectName("numberOfEnvelopsLabel")
            self.numberOfEnvelopsSpinBox = QSpinBox(self.factorOfSafetyGroupBox)
            self.numberOfEnvelopsSpinBox.setObjectName("numberOfEnvelopsSpinBox")
            group_box_fos_form_layout.addRow(self.numberOfEnvelopsLabel, self.numberOfEnvelopsSpinBox)
            #
            self.FOSTable = QTableWidget(self.factorOfSafetyGroupBox)
            self.FOSTable.setObjectName("FOSTable")
            group_box_fos_form_layout.addRow(self.FOSTable)
            #
            self.phaseToPlotComboBox = QComboBox(self)
            self.phaseToPlotComboBox.setObjectName("phaseToPlotComboBox")
            self.phaseToPlotLabel = QLabel(self)
            self.phaseToPlotLabel.setObjectName("phaseToPlotLabel")
            group_box_fos_form_layout.addRow(self.phaseToPlotLabel, self.phaseToPlotComboBox)
            #
            self.buttonBox = QDialogButtonBox(self)
            self.buttonBox.setObjectName("buttonBox")
            self.buttonBox.setOrientation(Qt.Horizontal)
            self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
            self.buttonBox.accepted.connect(self.accept)
            self.buttonBox.rejected.connect(self.reject)
            button_box_form_layout = QFormLayout()
            self.buttonBox.setLayout(button_box_form_layout)
            main_layout.addWidget(self.buttonBox)
            #
            self.setWindowTitle("Support Capacity Plot")
            self.supportElementLabel.setText("Support Element:")
            self.envelopeTypeLabel.setText("Envelope Type:")
            self.factorOfSafetyGroupBox.setTitle("Factor of Safety Envelopes")
            self.numberOfEnvelopsLabel.setText("Number of Envelopes:")
            self.phaseToPlotLabel.setText("Phase to Plot:")
            #
            # Fill support element
            self.supportElementComboBox.clear()
            self.supportElementComboBox.addItems(list(composite_sections.keys()))
            #
            # Fill envelop type
            envelope_type_list = [
                'Carranza-Torres & Diederichs'
            ]
            self.envelopeTypeComboBox.clear()
            self.envelopeTypeComboBox.addItems(envelope_type_list)
            #
            # Fill spinBox default value
            self.numberOfEnvelopsSpinBox.setValue(3)
            self.numberOfEnvelopsSpinBox.valueChanged.connect(self.update_table_size)
            #
            # Fill FOS table default values
            horizontal_headers = ['#', 'Factor of Safety']
            stylesheet = "QHeaderView::section{Background-color:rgb(221,221,221); border - radius: 14px;}"
            self.FOSTableValues = [1, 1.2, 1.4]
            self.number_fos_values = self.numberOfEnvelopsSpinBox.value()  # Should be 3
            prototype_item = QTableWidgetItem('')
            prototype_item.setTextAlignment(Qt.AlignCenter)
            self.FOSTable.setColumnCount(2)
            self.FOSTable.setItemPrototype(prototype_item)
            self.FOSTable.verticalHeader().setVisible(False)
            self.FOSTable.setColumnWidth(0, 100)
            self.FOSTable.horizontalHeader().setStretchLastSection(True)
            self.FOSTable.setStyleSheet(stylesheet)
            self.FOSTable.setHorizontalHeaderLabels(horizontal_headers)
            self.FOSTable.setRowCount(self.number_fos_values)
            for i in range(self.number_fos_values):
                first_column_item = QTableWidgetItem(str(i+1))
                first_column_item.setFlags(Qt.ItemIsEnabled)
                first_column_item.setTextAlignment(Qt.AlignCenter)
                second_column_item = QTableWidgetItem(str(self.FOSTableValues[i]))
                second_column_item.setTextAlignment(Qt.AlignCenter)
                self.FOSTable.setItem(i, 0, first_column_item)
                self.FOSTable.setItem(i, 1, second_column_item)
                self.FOSTable.item(i, 0).setBackground(QColor(221, 221, 221))
            self.FOSTable.cellClicked.connect(self.update_fos_values)
            self.FOSTable.show()

            # Fill phase to plot combo-box
            self.phaseToPlotComboBox.clear()
            phase_list = []
            for i in range(1, len(g_o.Phases)):
                phase_list.append(g_o.Phases[i].Identification.value)
            self.phaseToPlotComboBox.addItems(phase_list)

        def update_fos_values(self):
            for i in range(self.number_fos_values):
                try:
                    current_value = self.FOSTable.item(i, 1).text()
                    try:
                        self.FOSTableValues[i] = float(current_value)
                    except ValueError:
                        print("not a float")
                except Exception as e:
                    print(e)

        def update_table_size(self):
            new_number_fos_values = self.numberOfEnvelopsSpinBox.value()
            old_number_fos_values = self.number_fos_values
            self.FOSTable.setRowCount(new_number_fos_values)
            if new_number_fos_values < old_number_fos_values:
                del self.FOSTableValues[old_number_fos_values-1]
            else:
                self.FOSTableValues = self.FOSTableValues + [None]
            for i in range(new_number_fos_values):
                first_column_item = QTableWidgetItem(str(i+1))
                first_column_item.setFlags(Qt.ItemIsEnabled)
                first_column_item.setTextAlignment(Qt.AlignCenter)
                second_column_item = QTableWidgetItem(str(self.FOSTableValues[i]))
                second_column_item.setTextAlignment(Qt.AlignCenter)
                self.FOSTable.setItem(i, 0, first_column_item)
                self.FOSTable.item(i, 0).setBackground(QColor(221, 221, 221))
            self.number_fos_values = new_number_fos_values
            self.FOSTable.show()

    def Dibujo(selected_phase, section_name, path, envelope_type, fos):

        # Get PLAXIS global structural force results for chosen phase and composite section
        g_o.Plots[-1].PhaseBehaviour = "projectphase"
        g_o.Plots[-1].Phase = selected_phase
        has_material = check_platemat_existence(section_name)
        if not has_material:
            show_warning_dialog("Plate material "+section_name+" does not exist")
        has_failed, moment_tot, thrust_tot, shear_tot = get_moment_thrust_shear(section_name, selected_phase)
        #
        # Get  structural force results for each component: Shotcrete and steel
        compositeSections = dict(path)
        section_prop = compositeSections[section_name]
        component_results = redistribute(moment_tot, thrust_tot, shear_tot, section_prop)
        #
        # Calculate capacity envelopes for each user-defined factor of safety value
        capacity_envelops = envelops(section_prop, envelope_type, fos)
        #
        # Display results
        display_results(component_results, capacity_envelops, fos)
    #
    #
    ##############
    unitLength = g_o.GeneralInfo.UnitLength.value
    unitForce = g_o.GeneralInfo.UnitForce.value
    ##############
    #
    Dibujo(selected_phase, section_name, path, envelope_type, fos) #Se manda llamar a la función donde se alamcenaron los parametros

    # Obtener de PLAXIS los resultados globales de la fuerza estructural para la fase y el sostenimiento elegidas.
    g_o.Plots[-1].PhaseBehaviour = "projectphase" # Se define con un nombre a la fase
    g_o.Plots[-1].Phase = selected_phase #Se manda llamar ala variable
    has_material = check_platemat_existence(section_name) #Se revisa de que el material exista, si no existe produce un mensaje de error
    if not has_material:
        show_warning_dialog("Plate material "+section_name+" does not exist")
    #
    #print(f"phase0_s: {phase0_s}, x_point: {x_point}, shotcreteCompressiveStrength: {shotcreteCompressiveStrength}, shotcretePoissonRatio: {shotcretePoissonRatio}, shotcreteTensileStrength: {shotcreteTensileStrength}, shotcreteThickness: {shotcreteThickness}, shotcreteUnitWeight: {shotcreteUnitWeight}, shotcreteYoungModulus: {shotcreteYoungModulus}, steelSetArea: {steelSetArea}, steelSetCompressiveStrength: {steelSetCompressiveStrength}, steelSetInertia: {steelSetInertia}, steelSetPoissonRatio: {steelSetPoissonRatio}, steelSetSectionDepth: {steelSetSectionDepth}, steelSetSpacing: {steelSetSpacing}, steelSetTensileStrength: {steelSetTensileStrength}, steelSetYoungModulus: {steelSetYoungModulus}, steelUnitWeight: {steelUnitWeight}")

    
    #Se mandan llamar a las variables de los resultados momento, empuje y cortante, y se definen los resultados de las variables llamadas
    #para este caso se llamo a Lining y la fase 8
    has_failed, moment_tot, thrust_tot, shear_tot = get_moment_thrust_shear(section_name, selected_phase)
    #
    # Obtener resultados de fuerza estructural para cada componente: Concreto Lanzado y Acero
    compositeSections = dict(path)
    #Se llama a que lea el archivo donde se obtiene las propiedades del sostenimiento
    section_prop = compositeSections[section_name] #Se define la seccion compuesta
    #
    #Calcula los resultados de los momentos, empuje y cortante para la sección propuesta.
    component_results = redistribute(moment_tot, thrust_tot, shear_tot, section_prop) 
    #
    # Calcular envolventes de capacidad para cada valor de factor de seguridad definido.
    capacity_envelops = envelops(section_prop, envelope_type, fos)
    #
        
    from shapely.geometry import Point, Polygon #importa una libreria para dibujar puntos y poligonos

    def Resultados_FalsoVerdadero(fos_values,results,envelopes,fos_interes):  
        """
        Define una función con un nombre y se define una lista de parametros, despues se genera las instrucciones 
        que tendrá la funcion y regresa un resultado
        """
        #Recupera lo que hay que mostrar de los diccionarios
        # Resultados de los componentes, manda llamar del diccionario results de las listas asignadas
        moment_steel = results['steel']['m']
        thrust_steel = results['steel']['n']
        shear_steel = results['steel']['q']
        moment_shotcrete = results['shotcrete']['m']
        thrust_shotcrete = results['shotcrete']['n']
        shear_shotcrete = results['shotcrete']['q']
        #
        # Valores para obtener las envolventes, manda llamar del diccionario envelopes de las listas asignadas
        moment_thrust_steel_compression_envelopes = envelopes['steel']['mn']['comp']
        moment_thrust_steel_tension_envelopes = envelopes['steel']['mn']['tens']
        moment_thrust_shotcrete_compression_envelopes = envelopes['shotcrete']['mn']['comp']
        moment_thrust_shotcrete_tension_envelopes = envelopes['shotcrete']['mn']['tens']
        shear_force_thrust_steel_compression_envelopes = envelopes['steel']['qn']['comp']
        shear_force_thrust_steel_tension_envelopes = envelopes['steel']['qn']['tens']
        shear_force_thrust_shotcrete_compression_envelopes = envelopes['shotcrete']['qn']['comp']
        shear_force_thrust_shotcrete_tension_envelopes = envelopes['shotcrete']['qn']['tens']
        ##########
        # Mandar llamar la variable fos y asignarla a fos_values
        #fos_values = fos      
        def crear_poligonos(fos_values, compression_data, tension_data):
            fos_polygons = {}
            for fos_value, comp_data, tens_data in zip(fos_values, compression_data, tension_data):
                # Asegurarse de que comp_data y tens_data sean listas o tuplas
                comp_data = comp_data if isinstance(comp_data, (list, tuple)) else [comp_data]
                tens_data = tens_data if isinstance(tens_data, (list, tuple)) else [tens_data]
                X1G1, Y1G1 = comp_data
                X2G1, Y2G1 = tens_data
                X3G1 = np.concatenate((X1G1, X2G1[::-1]))
                Y3G1 = np.concatenate((Y1G1, Y2G1[::-1]))
                coords = [(X3G1[i], Y3G1[i]) for i in range(len(X3G1))]
                fos_polygons[fos_value] = Polygon(coords)
            return fos_polygons

        def contar_puntos_en_poligonos(momentos, empujes, fos_polygons):
            puntos_en_poligonos = {fos_value: 0 for fos_value in fos_polygons}
            puntos_fuera_de_ambos = 0
            for punto_coord in zip(momentos, empujes):
                punto = Point(punto_coord)
                en_algun_poligono = False
                for fos_value in reversed(fos_polygons):
                    poligono = fos_polygons[fos_value]
                    if poligono.contains(punto):
                        puntos_en_poligonos[fos_value] += 1
                        en_algun_poligono = True
                        break
                if not en_algun_poligono:
                    puntos_fuera_de_ambos += 1
            return puntos_en_poligonos, puntos_fuera_de_ambos

        def graficar_resultados(momentos, empujes, fos_polygons, title, variable):
            plt.figure()
            plt.scatter(momentos, empujes, label='Puntos', color='r', marker='o')
            for fos_value, poligono in fos_polygons.items():
                x, y = poligono.exterior.xy
                plt.plot(x, y, label=f'Polígono FOS {fos_value}')
            plt.xlabel(f'{variable} (kNm)' if variable == 'Momento' else f'{variable} (kN)')
            plt.ylabel('Empuje (kN)')
            plt.title(title)
            plt.legend()
            plt.show()

        # Imprimir resultados para la gráfica 1
        fos_polygons_1 = crear_poligonos(fos_values, moment_thrust_steel_compression_envelopes, moment_thrust_steel_tension_envelopes)
        puntos_en_poligonos_1, puntos_fuera_de_ambos_1 = contar_puntos_en_poligonos(moment_steel, thrust_steel, fos_polygons_1)
        for fos_value, puntos_en_poligono in puntos_en_poligonos_1.items():
            print(f"Total de puntos dentro del polígono FOS {fos_value}: {puntos_en_poligono}")
        print(f"Total de puntos fuera de ambos polígonos: {puntos_fuera_de_ambos_1}")
        # Crear la gráfica para la gráfica 1
        graficar_resultados(moment_steel, thrust_steel, fos_polygons_1, 'Grafica 1: Momento vs Empuje del Acero', 'Momento')

        # Imprimir resultados para la gráfica 2
        fos_polygons_2 = crear_poligonos(fos_values, moment_thrust_shotcrete_compression_envelopes, moment_thrust_shotcrete_tension_envelopes)
        puntos_en_poligonos_2, puntos_fuera_de_ambos_2 = contar_puntos_en_poligonos(moment_shotcrete, thrust_shotcrete, fos_polygons_2)
        for fos_value, puntos_en_poligono in puntos_en_poligonos_2.items():
            print(f"Total de puntos dentro del polígono FOS {fos_value}: {puntos_en_poligono}")
        print(f"Total de puntos fuera de ambos polígonos: {puntos_fuera_de_ambos_2}")
        # Crear la gráfica para la gráfica 2
        graficar_resultados(moment_shotcrete, thrust_shotcrete, fos_polygons_2, 'Grafica 2: Momento Vs Empuje del Concreto Lanzado', 'Momento')

        # Imprimir resultados para la gráfica 3
        fos_polygons_3 = crear_poligonos(fos_values, shear_force_thrust_steel_compression_envelopes, shear_force_thrust_steel_tension_envelopes)
        puntos_en_poligonos_3, puntos_fuera_de_ambos_3 = contar_puntos_en_poligonos(shear_steel, thrust_steel, fos_polygons_3)
        for fos_value, puntos_en_poligono in puntos_en_poligonos_3.items():
            print(f"Total de puntos dentro del polígono FOS {fos_value}: {puntos_en_poligono}")
        print(f"Total de puntos fuera de ambos polígonos: {puntos_fuera_de_ambos_3}")
        # Crear la gráfica para la gráfica 3
        graficar_resultados(shear_steel, thrust_steel, fos_polygons_3, 'Grafica 3: Empuje vs Cortante del Acero', 'Cortante')

        # Imprimir resultados para la gráfica 4
        fos_polygons_4 = crear_poligonos(fos_values, shear_force_thrust_shotcrete_compression_envelopes, shear_force_thrust_shotcrete_tension_envelopes)
        puntos_en_poligonos_4, puntos_fuera_de_ambos_4 = contar_puntos_en_poligonos(shear_shotcrete, thrust_shotcrete, fos_polygons_4)
        for fos_value, puntos_en_poligono in puntos_en_poligonos_4.items():
            print(f"Total de puntos dentro del polígono FOS {fos_value}: {puntos_en_poligono}")
        print(f"Total de puntos fuera de ambos polígonos: {puntos_fuera_de_ambos_4}")
        # Crear la gráfica para la gráfica 4
        graficar_resultados(shear_shotcrete, thrust_shotcrete, fos_polygons_4, 'Grafica 4: Empuje vs Cortante del Concreto Lanzado', 'Cortante')
        ##########
        # Filtrar resultados para el FOS de interés
        resultados_interes = {
            'grafica_1': {
                'puntos_en_poligonos': puntos_en_poligonos_1.get(fos_interes, 0),
                'puntos_fuera_de_ambos': puntos_fuera_de_ambos_1,
                'puntos_totales': len(moment_steel)
            },
            'grafica_2': {
                'puntos_en_poligonos': puntos_en_poligonos_2.get(fos_interes, 0),
                'puntos_fuera_de_ambos': puntos_fuera_de_ambos_2,
                'puntos_totales': len(moment_shotcrete)
            },
            'grafica_3': {
                'puntos_en_poligonos': puntos_en_poligonos_3.get(fos_interes, 0),
                'puntos_fuera_de_ambos': puntos_fuera_de_ambos_3,
                'puntos_totales': len(shear_steel)
            },
            'grafica_4': {
                'puntos_en_poligonos': puntos_en_poligonos_4.get(fos_interes, 0),
                'puntos_fuera_de_ambos': puntos_fuera_de_ambos_4,
                'puntos_totales': len(shear_shotcrete)
            },
        }
        return resultados_interes
        
    ##########
    ##########
    # Mandar llamar la variable fos y asignarla a fos_values
    fos_values = fos
    results = component_results
    envelopes = capacity_envelops
    fos_interes = 1.5
    resultados_fos_2 = Resultados_FalsoVerdadero(fos_values,results,envelopes,fos_interes)    

        # Acceder a los resultados para el FOS 1.5
    grafica_1_resultados = resultados_fos_2['grafica_1']
    print(f"Puntos en polígonos para la gráfica 1 y FOS 1.5: {grafica_1_resultados['puntos_en_poligonos']}")
    print(f"Puntos fuera de ambos polígonos para la gráfica 1 y FOS 1.5: {grafica_1_resultados['puntos_fuera_de_ambos']}")
    print(f"Puntos totales: {grafica_1_resultados['puntos_totales']}")

    grafica_2_resultados = resultados_fos_2['grafica_2']
    print(f"Puntos en polígonos para la gráfica 2 y FOS 1.5: {grafica_2_resultados['puntos_en_poligonos']}")
    print(f"Puntos fuera de ambos polígonos para la gráfica 2 y FOS 1.5: {grafica_2_resultados['puntos_fuera_de_ambos']}")
    print(f"Puntos totales: {grafica_2_resultados['puntos_totales']}")

    grafica_3_resultados = resultados_fos_2['grafica_3']
    print(f"Puntos en polígonos para la gráfica 3 y FOS 1.5: {grafica_3_resultados['puntos_en_poligonos']}")
    print(f"Puntos fuera de ambos polígonos para la gráfica 3 y FOS 1.5: {grafica_3_resultados['puntos_fuera_de_ambos']}")
    print(f"Puntos totales: {grafica_3_resultados['puntos_totales']}")

    grafica_4_resultados = resultados_fos_2['grafica_4']
    print(f"Puntos en polígonos para la gráfica 4 y FOS 1.5: {grafica_4_resultados['puntos_en_poligonos']}")
    print(f"Puntos fuera de ambos polígonos para la gráfica 4 y FOS 1.5: {grafica_4_resultados['puntos_fuera_de_ambos']}")
    print(f"Puntos totales: {grafica_4_resultados['puntos_totales']}")
   
    # Calcular porcentaje para la gráfica 1
    porcentaje_grafica_1 = (grafica_1_resultados['puntos_en_poligonos'] / grafica_1_resultados['puntos_totales']) * 100
    print(f"Porcentaje de puntos en polígonos para la gráfica 1 y FOS 1.5: {porcentaje_grafica_1}%")
    # Calcular porcentaje para la gráfica 2
    porcentaje_grafica_2 = (grafica_2_resultados['puntos_en_poligonos'] / grafica_2_resultados['puntos_totales']) * 100
    print(f"Porcentaje de puntos en polígonos para la gráfica 2 y FOS 1.5: {porcentaje_grafica_2}%")
    # Calcular porcentaje para la gráfica 3
    porcentaje_grafica_3 = (grafica_3_resultados['puntos_en_poligonos'] / grafica_3_resultados['puntos_totales']) * 100
    print(f"Porcentaje de puntos en polígonos para la gráfica 3 y FOS 1.5: {porcentaje_grafica_3}%")
    # Calcular porcentaje para la gráfica 4
    porcentaje_grafica_4 = (grafica_4_resultados['puntos_en_poligonos'] / grafica_4_resultados['puntos_totales']) * 100
    print(f"Porcentaje de puntos en polígonos para la gráfica 4 y FOS 1.5: {porcentaje_grafica_4}%")

    # Calcular totales globales
    total_puntos_en_poligonos = (
        grafica_1_resultados['puntos_en_poligonos'] +
        grafica_2_resultados['puntos_en_poligonos'] +
        grafica_3_resultados['puntos_en_poligonos'] +
        grafica_4_resultados['puntos_en_poligonos']
    )
    total_puntos_totales = (
        grafica_1_resultados['puntos_totales'] +
        grafica_2_resultados['puntos_totales'] +
        grafica_3_resultados['puntos_totales'] +
        grafica_4_resultados['puntos_totales']
    )

    # Calcular porcentaje global
    porcentajepyswarm = (total_puntos_en_poligonos / total_puntos_totales) * 100

    # Aplicar la condición
    if porcentajepyswarm < 100:
        porcentajepyswarm = 10000
    elif porcentajepyswarm == 100:
        porcentajepyswarm = 1000

    print("Resultado porcentajepyswarm", porcentajepyswarm)


    ############## Termina Codigo para las envolventes
    #Abrir el Visor de Outpot de Plaxis
    g_i.gotostages()
    phase7_s = g_i.Phases[-1]
    g_i.view(phase7_s)
    
    #Datos iniciales para las listas
    utotsost = []
    sum_mstagesost = []
    phaseordersost = [g_o.Phase_7]
   
    # Obtener los resultados de deformaciones y etapas
    # Iterar sobre cada fase y cada paso dentro de esa fase
    for phase in phaseordersost:
        for step in phase.Steps.value:
            utotsost.append(g_o.getcurveresults(g_o.Nodes[0],step,g_o.ResultTypes.Soil.Utot))
            sum_mstagesost.append(step.Reached.SumMstage.value)
            
    def getnodeid_result(phase, resulttype, nodeid):
        nodeindex = None
        resultLocation = 'Node'
        _resulttypeID = g_o.ResultTypes.Soil.NodeID
        _nodeids = g_o.getresults(phase, _resulttypeID, resultLocation)
        # use local list to find the index, otherwise an index command will be send to PLAXIS:
        nodeindex = _nodeids[:].index(nodeid)
        if nodeindex is not None:
            _resultvalues = g_o.getresults(phase, resulttype, resultLocation)
            _requestedvalue = _resultvalues[nodeindex]
            return _requestedvalue

        print('Could not find the requested node number in the results of this phase')
        return None
    def getnodeid_utot(phase, nodeid):
        """
        returns the result for Ux for the specific phase and node number
        """
        return getnodeid_result(phase, g_o.ResultTypes.Soil.Utot, nodeid)
    
    # set your input for the Phase reference and the selected node number
    phase_ref = g_o.Phase_7
    node_number = 7889
    # retrieve values
    utotnodo = getnodeid_utot(phase_ref, node_number)
    # Agrega los valores a las listas
    utot_values.append(utotnodo)
    # show the result
    print("Node {}: utot = {} m".format(node_number, utotnodo))
    
        # set your input for the Phase reference and the selected node number
    phase_ref = g_o.Phase_3
    node_number = 7889
    # retrieve values
    utotnodoinicio = getnodeid_utot(phase_ref, node_number)
    # Agrega los valores a las listas
    utot_values2.append(utotnodoinicio)
    # show the result
    print("Node {}: utot = {} m".format(node_number, utotnodoinicio))
    
    # Graficar los resultados
    #plt.figure(figsize=(10, 6))
    # Graficar utot en función de sum_mstage
    #plt.plot(sum_mstagesost, utotsost, marker='o', linestyle='-', color='b', label='Utot vs. SumMstage')
    #plt.title('Deformaciones Utot vs. Etapas SumMstage')
    #plt.xlabel('SumMstage')
    #plt.ylabel('Utot')
    #plt.legend()
    #plt.grid()
    #plt.show()
    
    utot.append(utot_values)
    utot2.append(utot_values2)
    
    s_o.close()
    
    #g_i.delete(phase4_s)
    #g_i.delete(phase5_s)
    #g_i.delete(phase6_s)
    #g_i.delete(phase7_s)

    s_o.close()
    # Espera un tiempo
    time.sleep(2)
    
    # Si porcentajepyswarm es 1000, sumar utotnodo * 1000
    if porcentajepyswarm == 1000:
        porcentajepyswarm += utotnodo * 1000
    # Mostrar el resultado final de porcentajepyswarm
    print("Resultado porcentajepyswarm cunado cumple la condicion 100%", porcentajepyswarm)

    # Devuelve el valor final del modelo
    return porcentajepyswarm

