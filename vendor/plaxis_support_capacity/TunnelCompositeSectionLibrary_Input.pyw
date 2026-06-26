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
With the PLAXIS 2D tunnel liner property definition the processes of calculating the equivalent plate properties in PLAXIS 2D input can be fully automated.

Instructions
------------
1. Download the package from Downloads below
2. Extract the zipped package and copy the content TunnelCompositeSectionLibrary_Input.pyw, TunnelSupportCapacityPlot_Output.pyw and shared.py files to:
	[PLAXIS 2D installation directory]\pytools\shared
3. In PLAXIS 2D Input, create the equivalent homogenized plate for the tunnel lining using the TunnelCompositeSectionLibrary_Input.pyw script
4. In the Expert menu, go to Expert > Run Python script > Open... browse for TunnelCompositeSectionLibrary_Input.pyw

This Python script is made available as a service to PLAXIS users and can only be used in combination with enabled
Geotechnical SELECT Entitlements.

Version
-------
Tested for PLAXIS 2D CONNECT Edition V22.02 with Python 3.8.10

"""
from plxscripting.easy import *
from PySide2.QtCore import *
from shared_composite_tunnel_support import *
import sys
import json
import os


class CompositeSectionProp:
    def __init__(self, name, unit_weight_steel, spacing_steel, area_steel, inertia_steel, young_modulus_steel,
                 poisson_ratio_steel, section_depth_steel, compressive_strength_steel, tensile_strength_steel,
                 unit_weight_shotcrete, thickness_shotcrete, young_modulus_shotcrete, poisson_ratio_shotcrete,
                 compressive_strength_shotcrete, tensile_strength_shotcrete):
        self.Name = name
        self.UnitWeightSteel = float(unit_weight_steel)
        self.SpacingSteel = float(spacing_steel)
        self.AreaSteel = float(area_steel)
        self.InertiaSteel = float(inertia_steel)
        self.YoungModulusSteel = float(young_modulus_steel)
        self.PoissonRatioSteel = float(poisson_ratio_steel)
        self.SectionDepthSteel = float(section_depth_steel)
        self.CompressiveStrengthSteel = float(compressive_strength_steel)
        self.TensileStrengthSteel = float(tensile_strength_steel)
        self.UnitWeightShotcrete = float(unit_weight_shotcrete)
        self.ThicknessShotcrete = float(thickness_shotcrete)
        self.YoungModulusShotcrete = float(young_modulus_shotcrete)
        self.PoissonRatioShotcrete = float(poisson_ratio_shotcrete)
        self.CompressiveStrengthShotcrete = float(compressive_strength_shotcrete)
        self.TensileStrengthShotcrete = float(tensile_strength_shotcrete)
        self.error_messages = []

    def validate(self):
        if not self.Name or self.Name.isspace():
            self.error_messages.append("Invalid composite section name.\n")
        if self.UnitWeightSteel < 0.:
            self.error_messages.append("Unit weight for steel sets should be positive.\n")
        if self.SpacingSteel < 0.:
            self.error_messages.append("Spacing between steel sets should be positive.\n")
        if self.AreaSteel < 0.:
            self.error_messages.append("Area of steel set should be positive.\n")
        if self.InertiaSteel < 0.:
            self.error_messages.append("Inertia of steel set should be positive.\n")
        if self.YoungModulusSteel <= 0.:
            self.error_messages.append("Young's modulus of steel set should be strictly positive.\n")
        if self.PoissonRatioSteel < 0 or self.PoissonRatioSteel > 0.5:
            self.error_messages.append("Steel Poisson ratio should be positive and less than 0.5.\n")
        if self.SectionDepthSteel <= 0.:
            self.error_messages.append("Section depth of steel set should be strictly positive.\n")
        if self.CompressiveStrengthSteel < 0.:
            self.error_messages.append("Steel compressive strength should be positive.\n")
        if self.TensileStrengthSteel < 0.:
            self.error_messages.append("Steel tensile strength should be positive.\n")
        if self.UnitWeightShotcrete < 0.:
            self.error_messages.append("Unit weight for shotcrete should be positive.\n")
        if self.ThicknessShotcrete <= 0.:
            self.error_messages.append("Shotcrete thickness should be strictly positive.\n")
        if self.YoungModulusShotcrete <= 0.:
            self.error_messages.append("Shotcrete Young's modulus should be strictly positive.\n")
        if self.PoissonRatioShotcrete < 0 or self.PoissonRatioShotcrete > 0.5:
            self.error_messages.append("Shotcrete Poisson ratio should be positive and less than 0.5.\n")
        if self.CompressiveStrengthShotcrete < 0.:
            self.error_messages.append("Shotcrete compressive strength should be positive.\n")
        if self.TensileStrengthShotcrete < 0.:
            self.error_messages.append("Shotcrete tensile strength should be positive.\n")
        return len(self.error_messages) == 0


class CompositeShellPropForm(QDialog):

    def __init__(self, library_dialog, edit_boolean, length_unit, force_unit, file_path,
                 initial_name, initial_values, current_composite_section, parent=None):
        super(CompositeShellPropForm, self).__init__(parent)
        self.current_composite_section = current_composite_section
        self.edit_boolean = edit_boolean
        self.currentName = initial_name
        self.force_unit = force_unit
        self.length_unit = length_unit
        self.composite_sections_file_path = file_path
        self.library_dialog = library_dialog
        #
        # Create widgets
        font = QFont()
        font.setPointSize(7)

        self.setObjectName("composite_shell_prop_dialog")
        self.setWindowTitle("Composite Shell Property")
        self.setEnabled(True)
        self.resize(420, 630)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.label_composite_section_name = QLabel(self)
        self.label_composite_section_name.setObjectName("label_composite_section_name")
        self.composite_section_name = QLineEdit(self)
        self.composite_section_name.setAlignment(Qt.AlignRight)
        self.composite_section_name.setObjectName("composite_section_name")
        self.label_composite_section_name.setText("Composite section name  ")

        top_form_layout = QFormLayout()
        top_form_layout.addRow(self.label_composite_section_name, self.composite_section_name)
        main_layout.addLayout(top_form_layout)

        self.groupBox_SteelSets = QGroupBox(self)
        self.groupBox_SteelSets.setObjectName("groupBox_SteelSets")
        self.groupBox_SteelSets.setTitle("Steel sets")
        group_box_steel_set_form_layout = QFormLayout()
        self.groupBox_SteelSets.setLayout(group_box_steel_set_form_layout)
        main_layout.addWidget(self.groupBox_SteelSets, 1)

        self.label_UnitWeightSteel = QLabel(self.groupBox_SteelSets)
        self.label_UnitWeightSteel.setObjectName("label_UnitWeightSteel")
        self.UnitWeightSteel = QLineEdit(self.groupBox_SteelSets)
        self.UnitWeightSteel.setObjectName("lineEdit_UnitWeightSteel")
        self.UnitWeightSteel.setAlignment(Qt.AlignRight)
        self.label_UnitWeightSteel.setText(f"Unit weight [{self.force_unit}/{self.length_unit}\u00B3]")
        group_box_steel_set_form_layout.addRow(self.label_UnitWeightSteel, self.UnitWeightSteel)

        self.label_Spacing = QLabel(self.groupBox_SteelSets)
        self.label_Spacing.setObjectName("label_Spacing")
        self.SpacingSteel = QLineEdit(self.groupBox_SteelSets)
        self.SpacingSteel.setObjectName("lineEdit_Spacing")
        self.SpacingSteel.setAlignment(Qt.AlignRight)
        self.label_Spacing.setText(f"Out-of-plane spacing [{self.length_unit}]")
        group_box_steel_set_form_layout.addRow(self.label_Spacing, self.SpacingSteel)

        self.label_AreaSteel = QLabel(self.groupBox_SteelSets)
        self.label_AreaSteel.setObjectName("label_AreaSteel")
        self.AreaSteel = QLineEdit(self.groupBox_SteelSets)
        self.AreaSteel.setObjectName("lineEdit_AreaSteel")
        self.AreaSteel.setAlignment(Qt.AlignRight)
        self.label_AreaSteel.setText(f"Area [{self.length_unit}\u00B2]")
        group_box_steel_set_form_layout.addRow(self.label_AreaSteel, self.AreaSteel)

        self.label_InertiaSteel = QLabel(self.groupBox_SteelSets)
        self.label_InertiaSteel.setObjectName("label_InertiaSteel")
        self.InertiaSteel = QLineEdit(self.groupBox_SteelSets)
        self.InertiaSteel.setObjectName("lineEdit_InertiaSteel")
        self.InertiaSteel.setAlignment(Qt.AlignRight)
        self.label_InertiaSteel.setText(f"Inertia [{self.length_unit}\u2074]")
        group_box_steel_set_form_layout.addRow(self.label_InertiaSteel, self.InertiaSteel)

        self.label_YoungModulusSteel = QLabel(self.groupBox_SteelSets)
        self.label_YoungModulusSteel.setObjectName("label_YoungModulusSteel")
        self.YoungModulusSteel = QLineEdit(self.groupBox_SteelSets)
        self.YoungModulusSteel.setObjectName("lineEdit_YoungModulusSteel")
        self.YoungModulusSteel.setAlignment(Qt.AlignRight)
        self.label_YoungModulusSteel.setText(f"Young's modulus [{self.force_unit}/{self.length_unit}\u00B2]")
        group_box_steel_set_form_layout.addRow(self.label_YoungModulusSteel, self.YoungModulusSteel)

        self.label_PoissonRatioSteel = QLabel(self.groupBox_SteelSets)
        self.label_PoissonRatioSteel.setObjectName("label_PoissonRatioSteel")
        self.PoissonRatioSteel = QLineEdit(self.groupBox_SteelSets)
        self.PoissonRatioSteel.setObjectName("lineEdit_PoissonRatioModulusSteel")
        self.PoissonRatioSteel.setAlignment(Qt.AlignRight)
        self.label_PoissonRatioSteel.setText("Poisson ratio")
        group_box_steel_set_form_layout.addRow(self.label_PoissonRatioSteel, self.PoissonRatioSteel)

        self.label_SectionDepthSteel = QLabel(self.groupBox_SteelSets)
        self.label_SectionDepthSteel.setObjectName("label_SectionDepthSteel")
        self.SectionDepthSteel = QLineEdit(self.groupBox_SteelSets)
        self.SectionDepthSteel.setObjectName("lineEdit_SectionDepthSteel")
        self.SectionDepthSteel.setAlignment(Qt.AlignRight)
        self.label_SectionDepthSteel.setText(f"Section depth [{self.length_unit}]")
        group_box_steel_set_form_layout.addRow(self.label_SectionDepthSteel, self.SectionDepthSteel)

        self.label_CompStrengthSteel = QLabel(self.groupBox_SteelSets)
        self.label_CompStrengthSteel.setObjectName("label_CompStrengthSteel")
        self.CompressiveStrengthSteel = QLineEdit(self.groupBox_SteelSets)
        self.CompressiveStrengthSteel.setObjectName("lineEdit_CompressiveStrengthSteel")
        self.CompressiveStrengthSteel.setAlignment(Qt.AlignRight)
        self.label_CompStrengthSteel.setText(f"Compressive strength [{self.force_unit}/{self.length_unit}\u00B2]  ")
        group_box_steel_set_form_layout.addRow(self.label_CompStrengthSteel, self.CompressiveStrengthSteel)

        self.label_TensileStrengthSteel = QLabel(self.groupBox_SteelSets)
        self.label_TensileStrengthSteel.setObjectName("label_TensileStrengthSteel")
        self.TensileStrengthSteel = QLineEdit(self.groupBox_SteelSets)
        self.TensileStrengthSteel.setObjectName("lineEdit_TensileStrengthSteel")
        self.TensileStrengthSteel.setAlignment(Qt.AlignRight)
        self.label_TensileStrengthSteel.setText(f"Tensile strength [{self.force_unit}/{self.length_unit}\u00B2]")
        group_box_steel_set_form_layout.addRow(self.label_TensileStrengthSteel, self.TensileStrengthSteel)

        self.groupBox_Shotcrete = QGroupBox(self)
        self.groupBox_Shotcrete.setObjectName("groupBox_Shotcrete")
        self.groupBox_Shotcrete.setTitle("Shotcrete")
        group_box_shotcrete_form_layout = QFormLayout(self)
        self.groupBox_Shotcrete.setLayout(group_box_shotcrete_form_layout)
        main_layout.addWidget(self.groupBox_Shotcrete, 1)

        self.label_UnitWeightShotcrete = QLabel(self.groupBox_Shotcrete)
        self.label_UnitWeightShotcrete.setObjectName("label_UnitWeightShotcrete")
        self.UnitWeightShotcrete = QLineEdit(self.groupBox_Shotcrete)
        self.UnitWeightShotcrete.setObjectName("lineEdit_UnitWeightShotcrete")
        self.UnitWeightShotcrete.setAlignment(Qt.AlignRight)
        self.label_UnitWeightShotcrete.setText(f"Unit weight [{self.force_unit}/{self.length_unit}\u00B3]")
        group_box_shotcrete_form_layout.addRow(self.label_UnitWeightShotcrete, self.UnitWeightShotcrete)

        self.label_ThicknessShotcrete = QLabel(self.groupBox_Shotcrete)
        self.label_ThicknessShotcrete.setObjectName("label_ThicknessShotcrete")
        self.ThicknessShotcrete = QLineEdit(self.groupBox_Shotcrete)
        self.ThicknessShotcrete.setObjectName("lineEdit_Thickness")
        self.ThicknessShotcrete.setAlignment(Qt.AlignRight)
        self.label_ThicknessShotcrete.setText(f"Thickness [{self.length_unit}]")
        group_box_shotcrete_form_layout.addRow(self.label_ThicknessShotcrete, self.ThicknessShotcrete)

        self.label_YoungModulusShotcrete = QLabel(self.groupBox_Shotcrete)
        self.label_YoungModulusShotcrete.setObjectName("label_YoungModulusShotcrete")
        self.YoungModulusShotcrete = QLineEdit(self.groupBox_Shotcrete)
        self.YoungModulusShotcrete.setObjectName("lineEdit_YoungModulusShotcrete")
        self.YoungModulusShotcrete.setAlignment(Qt.AlignRight)
        self.label_YoungModulusShotcrete.setText(f"Young's modulus [{self.force_unit}/{self.length_unit}\u00B2]")
        group_box_shotcrete_form_layout.addRow(self.label_YoungModulusShotcrete, self.YoungModulusShotcrete)

        self.label_PoissonRatioShotcrete = QLabel(self.groupBox_Shotcrete)
        self.label_PoissonRatioShotcrete.setObjectName("label_PoissonRatioShotcrete")
        self.PoissonRatioShotcrete = QLineEdit(self.groupBox_Shotcrete)
        self.PoissonRatioShotcrete.setObjectName("lineEdit_PoissonRatioShotcrete")
        self.PoissonRatioShotcrete.setAlignment(Qt.AlignRight)
        self.label_PoissonRatioShotcrete.setText("Poisson ratio")
        group_box_shotcrete_form_layout.addRow(self.label_PoissonRatioShotcrete, self.PoissonRatioShotcrete)

        self.label_CompStrengthShotcrete = QLabel(self.groupBox_Shotcrete)
        self.label_CompStrengthShotcrete.setObjectName("label_CompStrengthShotcrete")
        self.CompressiveStrengthShotcrete = QLineEdit(self.groupBox_Shotcrete)
        self.CompressiveStrengthShotcrete.setObjectName("lineEdit_CompressiveStrengthShotcrete")
        self.CompressiveStrengthShotcrete.setAlignment(Qt.AlignRight)
        self.label_CompStrengthShotcrete.setText(f"Compressive strength [{self.force_unit}/{self.length_unit}\u00B2]  ")
        group_box_shotcrete_form_layout.addRow(self.label_CompStrengthShotcrete, self.CompressiveStrengthShotcrete)

        self.label_TensileStrengthShotcrete = QLabel(self.groupBox_Shotcrete)
        self.label_TensileStrengthShotcrete.setObjectName("label_TensileStrengthShotcrete")
        self.TensileStrengthShotcrete = QLineEdit(self.groupBox_Shotcrete)
        self.TensileStrengthShotcrete.setObjectName("lineEdit_TensileStrengthShotcrete")
        self.TensileStrengthShotcrete.setAlignment(Qt.AlignRight)
        self.label_TensileStrengthShotcrete.setText(f"Tensile strength [{self.force_unit}/{self.length_unit}\u00B2]")
        group_box_shotcrete_form_layout.addRow(self.label_TensileStrengthShotcrete, self.TensileStrengthShotcrete)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonCancel = QDialogButtonBox.Cancel
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close | QDialogButtonBox.Ok)

        button_box_form_layout = QFormLayout()
        self.buttonBox.setLayout(button_box_form_layout)
        main_layout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        #
        self.composite_section_name.setText(initial_name)
        self.old_composite_section_name = initial_name
        self.UnitWeightSteel.setText(str(initial_values["steelUnitWeight"]))
        self.SpacingSteel.setText(str(initial_values["steelSetSpacing"]))
        self.AreaSteel.setText(str(initial_values["steelSetArea"]))
        self.InertiaSteel.setText(str(initial_values["steelSetInertia"]))
        self.YoungModulusSteel.setText(str(initial_values["steelSetYoungModulus"]))
        self.PoissonRatioSteel.setText(str(initial_values["steelSetPoissonRatio"]))
        self.SectionDepthSteel.setText(str(initial_values["steelSetSectionDepth"]))
        self.CompressiveStrengthSteel.setText(str(initial_values["steelSetCompressiveStrength"]))
        self.TensileStrengthSteel.setText(str(initial_values["steelSetTensileStrength"]))
        self.UnitWeightShotcrete.setText(str(initial_values["shotcreteUnitWeight"]))
        self.ThicknessShotcrete.setText(str(initial_values["shotcreteThickness"]))
        self.YoungModulusShotcrete.setText(str(initial_values["shotcreteYoungModulus"]))
        self.PoissonRatioShotcrete.setText(str(initial_values["shotcretePoissonRatio"]))
        self.CompressiveStrengthShotcrete.setText(str(initial_values["shotcreteCompressiveStrength"]))
        self.TensileStrengthShotcrete.setText(str(initial_values["shotcreteTensileStrength"]))

    def accept(self):

        file_path = self.composite_sections_file_path
        composite_section_prop = CompositeSectionProp(
            self.composite_section_name.text(),
            self.UnitWeightSteel.text(),
            self.SpacingSteel.text(),
            self.AreaSteel.text(),
            self.InertiaSteel.text(),
            self.YoungModulusSteel.text(),
            self.PoissonRatioSteel.text(),
            self.SectionDepthSteel.text(),
            self.CompressiveStrengthSteel.text(),
            self.TensileStrengthSteel.text(),
            self.UnitWeightShotcrete.text(),
            self.ThicknessShotcrete.text(),
            self.YoungModulusShotcrete.text(),
            self.PoissonRatioShotcrete.text(),
            self.CompressiveStrengthShotcrete.text(),
            self.TensileStrengthShotcrete.text()
        )

        if composite_section_prop.validate():
            is_updated = False
            if self.edit_boolean:
                found_platemat = check_plate_mat(g_i, composite_section_prop.Name)
                if found_platemat:
                    if self.currentName == composite_section_prop.Name:
                        updated_composite_sections = update_composite_section_library(
                            self.current_composite_section, composite_section_prop, self.currentName)
                        self.current_composite_section = updated_composite_sections
                        plate_param = convert_composite_section_to_plate_param(composite_section_prop)
                        self.currentName = composite_section_prop.Name
                        update_plate_materials(found_platemat, plate_param)
                        is_updated = True
                    else:
                        found_platemat, deleted_plate_mat = check_and_delete_platemat(g_i, composite_section_prop.Name)
                        if deleted_plate_mat:
                            updated_composite_sections = update_composite_section_library(
                                self.current_composite_section, composite_section_prop, self.currentName)
                            self.current_composite_section = updated_composite_sections
                            plate_param = convert_composite_section_to_plate_param(composite_section_prop)
                            self.currentName = composite_section_prop.Name
                            create_plate_materials(g_i, plate_param)
                            is_updated = True
                else:
                    updated_composite_sections = update_composite_section_library(
                        self.current_composite_section, composite_section_prop, self.currentName)
                    self.current_composite_section = updated_composite_sections
                    plate_param = convert_composite_section_to_plate_param(composite_section_prop)
                    self.currentName = composite_section_prop.Name
                    create_plate_materials(g_i, plate_param)
                    is_updated = True
            else:
                if composite_section_prop.Name in self.current_composite_section:
                    warning_msg = "Composite section " + composite_section_prop.Name + " already exists. \n" + \
                                  "Do you want to overwrite existing section?"
                    returned_value = show_warning_dialog(warning_msg)
                    if returned_value == QMessageBox.Cancel:
                        overwrite_agreement = False
                    else:
                        overwrite_agreement = True
                    # Create plate material
                    if overwrite_agreement:
                        plate_param = convert_composite_section_to_plate_param(composite_section_prop)
                        update_composite_section_library(
                            self.current_composite_section, composite_section_prop, composite_section_prop.Name)
                        delete_platemat(g_i, composite_section_prop.Name)
                        create_plate_materials(g_i, plate_param)
                        is_updated = True
                else:
                    if check_and_delete_platemat(g_i, composite_section_prop.Name):
                        plate_param = convert_composite_section_to_plate_param(composite_section_prop)
                        updated_composite_sections = add_to_composite_section_library(
                            self.current_composite_section, composite_section_prop)
                        self.current_composite_section = updated_composite_sections
                        create_plate_materials(g_i, plate_param)
                        is_updated = True
            if is_updated:
                update_json_file(self.current_composite_section, file_path)
                self.library_dialog.fill_list_widget(self.current_composite_section)
                self.close()
        else:
            show_error_dialog("\n".join(composite_section_prop.error_messages))


class CompositeSectionLibrary(QDialog):

    def __init__(self, current_composite_sections, length_unit, force_unit, file_path, parent=None):
        super(CompositeSectionLibrary, self).__init__(parent)
        #
        self.composite_shell_prop_dialog = None
        self.current_composite_sections = current_composite_sections
        self.length_unit = length_unit
        self.force_unit = force_unit
        self.composite_sections_file_path = file_path
        #
        # Create widgets
        self.setObjectName("CompositeSectionLibraryDialog")
        self.setWindowTitle("Composite Section Library")
        self.setEnabled(True)
        self.resize(280, 320)
        #
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        #
        self.compositeSectionGroupBox = QGroupBox(self)
        self.compositeSectionGroupBox.setObjectName("compositeSectionGroupBox")
        self.compositeSectionGroupBox.setEnabled(True)
        composite_section_group_box_form_layout = QFormLayout()
        self.compositeSectionGroupBox.setLayout(composite_section_group_box_form_layout)
        main_layout.addWidget(self.compositeSectionGroupBox)
        #
        self.listWidget = QListWidget(self.compositeSectionGroupBox)
        self.listWidget.setObjectName("listWidget")
        composite_section_group_box_form_layout.addRow(self.listWidget)
        #
        button_layout = QHBoxLayout()
        composite_section_group_box_form_layout.addRow(button_layout)
        #
        self.newButton = QPushButton()
        self.newButton.setObjectName("newButton")
        button_layout.addWidget(self.newButton)
        self.newButton.clicked.connect(self.on_new_clicked)
        self.editButton = QPushButton()
        self.editButton.setObjectName("editButton")
        button_layout.addWidget(self.editButton)
        self.editButton.clicked.connect(self.on_edit_clicked)
        self.copyButton = QPushButton()
        self.copyButton.setObjectName("copyButton")
        button_layout.addWidget(self.copyButton)
        self.copyButton.clicked.connect(self.on_copy_clicked)
        self.deleteButton = QPushButton()
        self.deleteButton.setObjectName("deleteButton")
        button_layout.addWidget(self.deleteButton)
        self.deleteButton.clicked.connect(self.on_delete_clicked)
        #
        # Fill list and set button names
        self.fill_list_widget(current_composite_sections)
        self.listWidget.setCurrentRow(0)
        self.listWidget.itemDoubleClicked.connect(self.on_edit_clicked)
        self.listWidget.itemDoubleClicked.connect(self.on_edit_clicked)
        #
        self.compositeSectionGroupBox.setTitle("Composite sections")
        self.editButton.setText("Edit")
        self.newButton.setText("New")
        self.copyButton.setText("Copy")
        self.deleteButton.setText("Delete")
        #
        #
        self.OKButton = QDialogButtonBox(self)
        self.OKButton.setObjectName("OKButton")
        self.OKButton.setOrientation(Qt.Horizontal)
        self.OKButton.setStandardButtons(QDialogButtonBox.Ok)
        self.OKButtonFormLayout = QFormLayout()
        self.OKButton.setLayout(self.OKButtonFormLayout)
        main_layout.addWidget(self.OKButton)
        #
        self.OKButton.accepted.connect(self.accept)
        self.OKButton.rejected.connect(self.reject)

    def on_new_clicked(self):
        composite_section_default_values = {}
        composite_section_name = ""
        composite_section_default_values["steelUnitWeight"] = 78.
        composite_section_default_values["steelSetSpacing"] = 1.
        composite_section_default_values["steelSetArea"] = 2.47E-3
        composite_section_default_values["steelSetInertia"] = 4.7e-6
        composite_section_default_values["steelSetYoungModulus"] = 200E6
        composite_section_default_values["steelSetPoissonRatio"] = 0.3
        composite_section_default_values["steelSetSectionDepth"] = 0.10
        composite_section_default_values["steelSetCompressiveStrength"] = 355E3
        composite_section_default_values["steelSetTensileStrength"] = 355E3
        composite_section_default_values["shotcreteUnitWeight"] = 24.
        composite_section_default_values["shotcreteThickness"] = 0.25
        composite_section_default_values["shotcreteYoungModulus"] = 10E6
        composite_section_default_values["shotcretePoissonRatio"] = 0.2
        composite_section_default_values["shotcreteCompressiveStrength"] = 45E3
        composite_section_default_values["shotcreteTensileStrength"] = 5E3
        current_composite_sections = self.current_composite_sections
        length_unit = self.length_unit
        force_unit = self.force_unit
        file_path = self.composite_sections_file_path
        edit_boolean = False
        self.composite_shell_prop_dialog = CompositeShellPropForm(
            self, edit_boolean, length_unit, force_unit, file_path, composite_section_name,
            composite_section_default_values, current_composite_sections)
        self.composite_shell_prop_dialog.show()
        self.listWidget.setCurrentRow(0)

    def on_edit_clicked(self):
        composite_section_name = self.listWidget.currentItem().text()
        current_composite_sections = self.current_composite_sections
        length_unit = self.length_unit
        force_unit = self.force_unit
        file_path = self.composite_sections_file_path
        composite_section_default_values = current_composite_sections[composite_section_name]
        edit_boolean = True
        self.composite_shell_prop_dialog = CompositeShellPropForm(
            self, edit_boolean, length_unit, force_unit, file_path, composite_section_name,
            composite_section_default_values, current_composite_sections)
        self.composite_shell_prop_dialog.show()
        self.listWidget.setCurrentRow(0)

    def on_copy_clicked(self):
        selected_composite_section_name = self.listWidget.currentItem().text()
        current_composite_sections = self.current_composite_sections
        length_unit = self.length_unit
        force_unit = self.force_unit
        file_path = self.composite_sections_file_path
        composite_section_default_values = current_composite_sections[selected_composite_section_name]
        edit_boolean = False
        composite_section_name = ""
        self.composite_shell_prop_dialog = CompositeShellPropForm(
            self, edit_boolean, length_unit, force_unit, file_path, composite_section_name,
            composite_section_default_values, current_composite_sections)
        self.composite_shell_prop_dialog.show()
        self.listWidget.setCurrentRow(0)

    def on_delete_clicked(self):
        composite_section_name = self.listWidget.currentItem().text()
        composite_sections = self.current_composite_sections
        file_path = self.composite_sections_file_path
        new_composite_sections = remove_from_composite_section_library(composite_sections, composite_section_name)
        delete_platemat(g_i, composite_section_name)
        self.fill_list_widget(new_composite_sections)
        update_json_file(new_composite_sections, file_path)
        self.current_composite_sections = new_composite_sections
        self.listWidget.setCurrentRow(0)

    def fill_list_widget(self, section_list):
        self.listWidget.clear()
        for key in section_list:
            self.listWidget.addItem(key)
        self.editButton.setEnabled(True)
        self.copyButton.setEnabled(True)
        self.deleteButton.setEnabled(True)
        if self.listWidget.count() == 0:
            self.editButton.setEnabled(False)
            self.copyButton.setEnabled(False)
            self.deleteButton.setEnabled(False)


def create_empty_json_file(file_path):
    data = {}
    with open(file_path, "w") as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)
    outfile.close()


def update_json_file(section_dict, file_path):
    with open(file_path, 'w') as outfile:
        # Reading from json file
        json.dump(section_dict, outfile, indent=4, sort_keys=True)
    outfile.close()


def remove_from_composite_section_library(composite_sections, to_be_removed_name):
    del composite_sections[to_be_removed_name]
    return sort_dictionary(composite_sections)


def update_composite_section_library(composite_sections, prop, old_name):
    del composite_sections[old_name]
    new_composite_section = {
        'steelUnitWeight': prop.UnitWeightSteel,
        'steelSetSpacing': prop.SpacingSteel,
        'steelSetArea': prop.AreaSteel,
        'steelSetInertia': prop.InertiaSteel,
        'steelSetYoungModulus': prop.YoungModulusSteel,
        'steelSetPoissonRatio': prop.PoissonRatioSteel,
        'steelSetSectionDepth': prop.SectionDepthSteel,
        'steelSetCompressiveStrength': prop.CompressiveStrengthSteel,
        'steelSetTensileStrength': prop.TensileStrengthSteel,
        'shotcreteUnitWeight': prop.UnitWeightShotcrete,
        'shotcreteThickness': prop.ThicknessShotcrete,
        'shotcreteYoungModulus': prop.YoungModulusShotcrete,
        'shotcretePoissonRatio': prop.PoissonRatioShotcrete,
        'shotcreteCompressiveStrength': prop.CompressiveStrengthShotcrete,
        'shotcreteTensileStrength': prop.TensileStrengthShotcrete
    }
    composite_sections[prop.Name] = new_composite_section
    return sort_dictionary(composite_sections)


def add_to_composite_section_library(composite_sections, prop):
    new_composite_section = {
        'steelUnitWeight': prop.UnitWeightSteel,
        'steelSetSpacing': prop.SpacingSteel,
        'steelSetArea': prop.AreaSteel,
        'steelSetInertia': prop.InertiaSteel,
        'steelSetYoungModulus': prop.YoungModulusSteel,
        'steelSetPoissonRatio': prop.PoissonRatioSteel,
        'steelSetSectionDepth': prop.SectionDepthSteel,
        'steelSetCompressiveStrength': prop.CompressiveStrengthSteel,
        'steelSetTensileStrength': prop.TensileStrengthSteel,
        'shotcreteUnitWeight': prop.UnitWeightShotcrete,
        'shotcreteThickness': prop.ThicknessShotcrete,
        'shotcreteYoungModulus': prop.YoungModulusShotcrete,
        'shotcretePoissonRatio': prop.PoissonRatioShotcrete,
        'shotcreteCompressiveStrength': prop.CompressiveStrengthShotcrete,
        'shotcreteTensileStrength': prop.TensileStrengthShotcrete
    }
    composite_sections[prop.Name] = new_composite_section
    return sort_dictionary(composite_sections)


def sort_dictionary(section_dict):
    sorted_dict = {key: value for key, value in sorted(section_dict.items())}
    return sorted_dict


def convert_composite_section_to_plate_param(section_prop):
    #
    plate_param = {}
    #
    d_st = (section_prop.YoungModulusSteel * section_prop.AreaSteel) / \
           (1 - section_prop.PoissonRatioSteel ** 2)
    d_sh = (section_prop.YoungModulusShotcrete * section_prop.ThicknessShotcrete) / \
           (1 - section_prop.PoissonRatioShotcrete ** 2)
    #
    k_st = (section_prop.YoungModulusSteel * section_prop.InertiaSteel) / \
           (1 - section_prop.PoissonRatioSteel ** 2)
    k_sh = (section_prop.YoungModulusShotcrete * section_prop.ThicknessShotcrete ** 3) / \
           (12 * (1 - section_prop.PoissonRatioShotcrete ** 2))
    #
    # Property
    plate_param["Identification"] = section_prop.Name
    plate_param["MaterialType"] = 1  # Elastic
    plate_param["EA1"] = d_st / section_prop.SpacingSteel + d_sh
    plate_param["EI"] = k_st / section_prop.SpacingSteel + k_sh
    plate_param["StructNu"] = 0.
    plate_param["W"] = section_prop.UnitWeightShotcrete * section_prop.ThicknessShotcrete + \
        section_prop.UnitWeightSteel * section_prop.AreaSteel / section_prop.SpacingSteel

    return plate_param


def create_plate_materials(g, plate_param):
    parameters = []
    for key in plate_param.keys():
        parameters.append((key, plate_param[key]))
    g.platemat(*parameters)


def update_plate_materials(platemat, plate_param):
    for key in plate_param.keys():
        setattr(platemat, key, plate_param[key])


def delete_platemat(g, name):
    for mat in g.Materials:
        if mat.TypeName.value == 'PlateMat':
            if mat.Identification == name:
                g.delete(mat)


def check_and_delete_platemat(g, name):
    deleted = False
    found = False

    for mat in g.Materials:
        if mat.TypeName.value == 'PlateMat':
            if mat.Identification == name:
                found = True
                warning_msg = "Material name " + name + " already exists. Do you want to overwrite existing material?"
                return_value = show_warning_dialog(warning_msg)
                if return_value == QMessageBox.Ok:
                    deleted = True
                    g.delete(mat)

    return found, deleted


def check_plate_mat(g, name):
    found = None

    for mat in g.Materials:
        if mat.TypeName.value == 'PlateMat':
            if mat.Identification == name:
                found = mat

    return found


# Initialize input scripting server
s_i, g_i = new_server()

workingDir = g_i.Project.DataDir.value
if workingDir == "":
    workingDir = get_default_working_dir(s_i)

unitLengthEnum = {'m': 2, 'yd': 6, 'mm': 0, 'km': 3, 'in': 4, 'ft': 5, 'cm': 1}
unitLengthValue = g_i.Project.UnitLength.value
unitForceEnum = {'lbf': 3, 'kip': 4, 'N': 0, 'MN': 2, 'kN': 1}
unitForceValue = g_i.Project.UnitForce.value
lengthUnit = [unit for unit in unitLengthEnum if unitLengthEnum[unit] == unitLengthValue][0]
forceUnit = [unit for unit in unitForceEnum if unitForceEnum[unit] == unitForceValue][0]

app = QApplication([])
set_program_toolbar_icon(app)

# Read-in possibly existing composite section library
composite_sections_file_path = workingDir + 'compositeSections.json'
a = os.path.exists(composite_sections_file_path)
if not os.path.exists(composite_sections_file_path):
    create_empty_json_file(composite_sections_file_path)
compositeSectionDict = read_json_file(composite_sections_file_path)

# Create and show the form
InputWindow = CompositeSectionLibrary(compositeSectionDict, lengthUnit, forceUnit, composite_sections_file_path)
InputWindow.show()

# Run the main Qt loop
sys.exit(app.exec_())
