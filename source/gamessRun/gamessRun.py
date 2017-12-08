#!/usr/bin/python3
from reference.reference import *
import logging
import os
import shutil
import subprocess


# TODO: set up logging as module-specific
def process_data(input_file, number_of_processors=4):
    name = input_file.split("Input.inp")[0]
    output_name = name + "Output.log"

    input_directory = os.getcwd()

    # Copy input file to gamess directory
    try:
        logging.debug("Copying input data file to gamess directory.")
        shutil.copyfile(os.path.join(input_directory, input_file),
                        os.path.join(SysReference.PATH_TO_GAMESS, input_file))
    except FileNotFoundError:
        logging.error("{} not found in gamess directory. Moving to next file.")
        return

    os.chdir(SysReference.PATH_TO_GAMESS)

    remove_residuals(name)

    # Run gamess job
    logging.info("Beginning gamess process.")
    output_log = open(output_name, 'w')
    subprocess.call(["./rungms", input_file, SysReference.VERSION,
                     str(number_of_processors)], stdout=output_log)
    output_log.close()
    logging.info("gamess process complete.")

    # Clean up files from run and copy output to input directory
    try:
        os.remove(os.path.join(SysReference.PATH_TO_GAMESS, input_file))
        shutil.copyfile(os.path.join(SysReference.PATH_TO_GAMESS, output_name),
                        os.path.join(input_directory, output_name))
        logging.info("Output file copied to starting directory.")
        os.remove(os.path.join(SysReference.PATH_TO_GAMESS, output_name))
    except FileNotFoundError:
        logging.warning("Output file not found.")
    finally:
        os.chdir(input_directory)  # Return to input directory for next job


def remove_residuals(name):
    # Check for and remove all residual files from previous gamess runs
    supp_out_files = os.listdir(SysReference.SUPP_OUTPUT_DIR)
    for file in supp_out_files:
        if file.startswith(name):
            os.remove(os.path.join(SysReference.SUPP_OUTPUT_DIR, file))
            logging.warning("Removed {} from supplemental output directory."
                            .format(file))

    temp_binary_files = os.listdir(SysReference.TEMP_BINARY_DIR)
    for file in temp_binary_files:
        if file.startswith(name):
            os.remove(os.path.join(SysReference.TEMP_BINARY_DIR, file))
            logging.warning("Removed {} from temporary binary directory."
                            .format(file))
