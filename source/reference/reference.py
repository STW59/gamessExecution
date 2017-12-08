#!/usr/bin/python3
class SysReference:
    # TODO: build sys_reference from settings file
    settings_file = open("settings.dat", "r")
    for line in settings_file:
        if line.startswith("$"):
            pass
        elif line.startswith("path_to_gamess"):
            PATH_TO_GAMESS = line.split("= ")[1][:-2]
        elif line.startswith("temporary_binary_directory"):
            TEMP_BINARY_DIR = line.split("= ")[1][:-2]
        elif line.startswith("supplemental_output_directory"):
            SUPP_OUTPUT_DIR = line.split("= ")[1][:-2]
        elif line.startswith("gamess_version"):
            VERSION = line.split("= ")[1][:-2]
        else:
            pass
    settings_file.close()
