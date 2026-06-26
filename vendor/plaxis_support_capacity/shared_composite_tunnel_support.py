import json
import sys
import os
import py_package_decryptor
from plxscripting.plaxis_connector import find_path_from_registry_for_connect_edition
from PySide2.QtWidgets import *
from PySide2.QtGui import *


def get_plx_path(app='Plaxis2D', versions=None):
    """
    uses the plxscripting plaxis connector to find the applications installation path
    :param app: name of the application: Plaxis2D or Plaxis3D, default is Plaxis2D
    :param versions: list of version numbers (int) to search for, default is [23, 22, 21]
    :return: PLAXIS program folder path
    """
    if versions is None:
        versions = [23, 22, 21]
    for _version in versions:
        plx2d = find_path_from_registry_for_connect_edition(app, _version)
        if plx2d:
            return plx2d
    return None


def add_plx_pythonlib_to_syspath():
    """
    adds the plaxis tools pythonlib path to the current sys path
    """
    plx_path = get_plx_path()
    if plx_path:
        sub_path = r'tools\pythonlib'
        tools_path = os.path.join(plx_path, sub_path)
        if os.path.exists(tools_path):
            sys.path.append(tools_path)


#
# plaxis tools imports
add_plx_pythonlib_to_syspath()
try:
    # import from tools/py from installed program folder
    # noinspection PyUnresolvedReferences
    from ui.image_resources.constants import ICON_TECH_PREVIEW_PATH, ICON_GREEN_OK_PATH, \
        ICON_OK_PATH, ICON_MANUALS_PATH, ICON_REFRESH_PATH
    import ui.image_resources.resources
except (ImportError, ModuleNotFoundError) as error:
    # Output expected ImportErrors
    print("Failed ui import")
    print(error.__class__.__name__ + ": " + str(error))


def set_program_toolbar_icon(app):
    try:
        app_icon = QIcon(ICON_TECH_PREVIEW_PATH)
        app.setWindowIcon(app_icon)
    except NameError:
        print("Issue in adding an icon! icon not added")


def get_default_working_dir(s) -> object:
    if s.is_2d:
        working_dir = os.environ['TEMP'] + '\\' + 'Plaxis2DXTemp\\'
    else:
        working_dir = os.environ['TEMP'] + '\\' + 'Plaxis3DTemp\\'
    return working_dir


def read_json_file(fil_dir):
    try:
        with open(fil_dir, 'r') as openfile:
            # Reading from json file
            file_list = json.load(openfile)
            return file_list
    except FileNotFoundError:
        show_error_dialog('File '+fil_dir+' cannot be found!')
        sys.exit()
    except json.JSONDecodeError:
        show_error_dialog('File '+fil_dir+' seems to be corrupted!')
        sys.exit()


def show_error_dialog(error_message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(error_message)
    msg_box.setWindowTitle("Error")
    msg_box.setStandardButtons(QMessageBox.Cancel)
    msg_box.exec()


def show_warning_dialog(warning_message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(warning_message)
    msg_box.setWindowTitle("Warning")
    msg_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
    return_value = msg_box.exec()
    return return_value


