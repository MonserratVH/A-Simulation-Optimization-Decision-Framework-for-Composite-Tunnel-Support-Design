"""
Copyright (c) Plaxis bv. All rights reserved.

Unless explicitly acquired and licensed from Licensor under another
license, the contents of this file are subject to the Plaxis Public
License ("PPL") Version 1.0, or subsequent versions as allowed by the PPL,
and You may not copy or use this file in either source code or executable
form, except in compliance with the terms and conditions of the PPL.

All software distributed under the PPL is provided strictly on an "AS
IS" basis, WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, AND
LICENSOR HEREBY DISCLAIMS ALL SUCH WARRANTIES, INCLUDING WITHOUT
LIMITATION, ANY WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE, QUIET ENJOYMENT, OR NON-INFRINGEMENT. See the PPL for specific
language governing rights and limitations under the PPL.

How to define composite section plate properties and evaluate tunnel liner capacity with PLAXIS
-----------------------------------
With the PLAXIS 2D capacity evaluation tools, the processes of displaying support capacity plots in PLAXIS 2D Output can be fully automated.

Instructions
------------
1. Download the package from Downloads below
2. Extract the zipped package and copy the content TunnelCompositeSectionLibrary_Input.pyw, TunnelSupportCapacityPlot_Output.pyw and shared.py files to:
	[PLAXIS 2D installation directory]\pytools\shared
3. In PLAXIS 2D Output, the support capacity plots for previously defined tunnel linings can be drawn using the TunnelSupportCapacityPlot_Output.pyw script
4. In the Expert menu, go to Expert > Run Python script > Open... browse for TunnelSupportCapacityPlot_Output.pyw

This Python script is made available as a service to PLAXIS users and can only be used in combination with enabled
Geotechnical SELECT Entitlements.

Version
-------
Tested for PLAXIS 2D CONNECT Edition V22.02 with Python 3.8.10

"""
from plxscripting.easy import *
from PySide2.QtCore import *
from shared_composite_tunnel_support import *
import matplotlib.pyplot as plt
import os
import sys
import numpy as np


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

    for plateCluster in g_o.Plates:
        for plate in plateCluster:
            if plate.Material.Identification == section_name:
                try:
                    m = g_o.getresults(plate, phase, g_o.ResultTypes.Plate.M2D, "node")
                except Exception as e:
                    error_message = f"Could not get moment results for plate {section_name} " \
                                    f"in phase {phase.Identification.value}\n[{e}]"
                    show_error_dialog(error_message)
                    has_failed = True
                    break
                results_moment = results_moment + [x for x in m]
                try:
                    n = g_o.getresults(plate, phase, g_o.ResultTypes.Plate.Nx2D, "node")
                except Exception as e:
                    error_message = f"Could not get normal force results for plate {section_name} " \
                                    f"in phase {phase.Identification.value}\n[{e}]"
                    show_error_dialog(error_message)
                    has_failed = True
                    break
                results_thrust = results_thrust + [x for x in n]
                try:
                    s = g_o.getresults(plate, phase, g_o.ResultTypes.Plate.Q2D, "node")
                except Exception:
                    error_message = "Could not get shear force results for plate \"" \
                                    + section_name +\
                                    "\" in phase "\
                                    + phase.Identification.value
                    show_error_dialog(error_message)
                    has_failed = True
                    break
                results_shear = results_shear + [x for x in s]

    return has_failed, results_moment, results_thrust, results_shear


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
    set_program_toolbar_icon(plt.get_current_fig_manager().window)
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

    def accept(self):

        #
        # Get PLAXIS global structural force results for chosen phase and composite section
        g_o.Plots[-1].PhaseBehaviour = "projectphase"
        for phase in g_o.Phases:
            if phase.Identification.value == self.phaseToPlotComboBox.currentText():
                selected_phase = phase
                break
        g_o.Plots[-1].Phase = selected_phase
        section_name = self.supportElementComboBox.currentText()
        has_material = check_platemat_existence(section_name)
        if not has_material:
            show_warning_dialog("Plate material "+section_name+" does not exist")
        has_failed, moment_tot, thrust_tot, shear_tot = get_moment_thrust_shear(section_name, selected_phase)
        #
        # Get  structural force results for each component: Shotcrete and steel
        section_prop = self.compositeSections[section_name]
        component_results = redistribute(moment_tot, thrust_tot, shear_tot, section_prop)
        #
        # Calculate capacity envelopes for each user-defined factor of safety value
        envelope_type = self.envelopeTypeComboBox.currentText()
        fos = self.FOSTableValues
        capacity_envelops = envelops(section_prop, envelope_type, fos)
        #
        # Display results
        display_results(component_results, capacity_envelops, fos)


#
# plaxis tools imports
add_plx_pythonlib_to_syspath()

# Initialize input scripting server
s_o, g_o = new_server()
#
unitLength = g_o.GeneralInfo.UnitLength.value
unitForce = g_o.GeneralInfo.UnitForce.value

section_libraryPathName = g_o.GeneralInfo.Filename.value
if section_libraryPathName.split('.')[0] == "":
    section_libraryRepoDir = get_default_working_dir(s_o)
else:
    dirName = os.path.dirname(section_libraryPathName)
    basename_without_ext = os.path.splitext(os.path.basename(section_libraryPathName))[0]
    if s_o.is_2d:
        dirExt = '.p2dxdat'
    else:
        dirExt = '.p3dat'
    section_libraryRepoDir = dirName + '\\' + basename_without_ext + dirExt + '\\'

app = QApplication([])
set_program_toolbar_icon(app)
compositeSections = read_json_file(section_libraryRepoDir + '\\compositeSections.json')

# Create and show the form
InputWindow = SupportCapacityPlotDB(compositeSections)
InputWindow.show()
# Run the main Qt loop
sys.exit(app.exec_())
