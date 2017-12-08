#!/usr/bin/python3
from basisSets.correlationConsistent import *
from basisSets.pople import *
from basisSets.polarizationConsistent import *
from gamessRun.gamessRun import *

import datetime
import logging
import os
import sys
import time


# Logging constants
DATETIME = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
LOGGING_LEVEL = logging.INFO

# Program constants
BASIS_SET = "Pople"
# BASIS_SET = "Correlation"
# BASIS_SET = "Polarization"


def build_data_sets():
    data_sets = []
    processed_data_sets = []
    input_dir_list = os.listdir(os.getcwd())

    # Put gamess input and log files into data structures for processing
    for file in input_dir_list:
        if file.endswith(".inp"):
            data_sets.append(file)
        elif file.endswith(".log"):
            processed_data_sets.append(file)
    logging.debug("Input read complete.")

    # Check to see if file was processed (check .inp against .log)
    for data_set in data_sets:
        if (data_set.split("Input.inp")[0] + "Output.log") in processed_data_sets:
            data_sets.remove(data_set)
            logging.info("{} already processed. Removing from queue."
                         .format(data_set))
    data_sets.sort()
    logging.debug("Processed files removed from queue.")
    return data_sets


def build_next_input(name, basis_set_index, next_basis_set):
    gamess_output_name = name + "Output.log"
    new_input_name = name + str(basis_set_index) + "-Input.inp"
    old_input_name = name + "Input.inp"

    # Read required data from files
    gamess_header = read_gamess_header(old_input_name)
    atom_coords = read_atom_coords(gamess_output_name)

    # Open new input file
    new_input_file = open(new_input_name, 'w')

    # Write new gamess input file
    header_line_index = 0
    for header_line in gamess_header:
        if "$BASIS" in header_line:
            new_line = " $BASIS GBASIS={} NGAUSS={} " \
                .format(selected_basis_set[next_basis_set][0],
                        selected_basis_dict[next_basis_set][1])

            # Add heavy atom polarization
            if "d" in next_basis_set:
                new_line += "NDFUNC={} ".format(selected_basis_dict[next_basis_set][2])

            # Add hydrogen polarization
            if "p" in next_basis_set:
                new_line += "NPFUNC={} ".format(selected_basis_dict[next_basis_set][3])

            # Add heavy atom diffuse functions
            if "+" in next_basis_set:
                new_line += "DIFFSP={} ".format(selected_basis_dict[next_basis_set][4])

            # Add hydrogen diffuse functions
            if "++" in next_basis_set:
                new_line += "DIFFS={} ".format(selected_basis_dict[next_basis_set][5])

            new_line += "$END\n"
        elif "$CONTRL" in header_line:
            new_line = " $CONTRL SCFTYP=RHF RUNTYP=OPTIMIZE DFTTYP=B3LYP "

            # Convert from cartesian to internal coordinates
            # if basis_set_index == len(selected_basis_set)-1:
            #     new_line += "COORD=ZMT "

            new_line += "$END\n"
        elif header_line_index == len(gamess_header) - 2:
            # Append latest basis set to title
            new_line = header_line.split("\n")[0] + " " + next_basis_set + "\n"
        else:
            new_line = header_line

        new_input_file.write(new_line)
        header_line_index += 1

    coord_line = 0
    for coordinate in atom_coords:
        if coord_line > 2:
            new_input_file.write(coordinate[1:])
        coord_line += 1

    new_input_file.write(" $END")
    new_input_file.close()


def gamess_optimization():
    batch_start_time = time.time()
    # Set up log file for batch process.
    # NOTE: this is different than the gamess .log files.
    log_filename = DATETIME + ".log"

    file_out = logging.FileHandler(log_filename)
    console_out = logging.StreamHandler()
    handlers = [file_out, console_out]
    logging.basicConfig(level=LOGGING_LEVEL,
                        format='%(asctime)s: %(levelname)s: %(message)s',
                        handlers=handlers)

    logging.info("Beginning log for batch started {}."
                 .format(DATETIME.replace("_", ":")))

    # Set basis set
    set_basis_set()

    # Read all files in working directory
    data_sets = build_data_sets()

    # Run each unprocessed input file
    for input_file in data_sets:
        # Generates gamess inputs for each of the given basis sets
        # Subsequently runs the gamess calculations for the inputs
        basis_set_index = 0
        for basis_set in selected_basis_set:
            logging.info("Beginning gamess job for {} with {} basis set."
                         .format(input_file, basis_set))

            start_time = time.time()
            process_data(input_file, 4)
            end_time = time.time()

            logging.info("gamess job for {} complete.".format(input_file))
            logging.info("Run time: {} hours.".
                         format((end_time - start_time) / (60 * 60)))

            # Create new gamess inputs for next basis set
            try:
                # Determine next basis set
                basis_set_index += 1
                next_basis_set = selected_basis_set[basis_set_index]
            except IndexError:
                logging.info("All basis sets complete.")
                # Process next data set
                continue

            # Determine file names
            name = input_file.split("Input.inp")[0]
            new_input_name = name + str(basis_set_index) + "-Input.inp"
            gamess_output_name = name + "Output.log"

            # Check to see if gamess "exited gracefully"
            exited_gracefully = False
            gamess_output_file = open(gamess_output_name, 'r')
            for output_line in gamess_output_file:
                if "exited gracefully" in output_line:
                    exited_gracefully = True
            gamess_output_file.close()
            if not exited_gracefully:
                logging.warning("gamess did not exit gracefully.")
                logging.warning("Check the gamess output file for details.")
                logging.warning("Continuing to next input file.")
                break

            # Build next GAMESS input file
            logging.info("Generating input for {} basis set.".format(next_basis_set))
            build_next_input(name, basis_set_index, next_basis_set)
            logging.info("Input generation complete.")

            input_file = new_input_name

    batch_end_time = time.time()
    logging.info("Batch process complete.")
    logging.info("Total batch processing time: {} hours"
                 .format((batch_end_time - batch_start_time) / (60 * 60)))


def read_atom_coords(gamess_output_name):
    gamess_output = open(gamess_output_name, 'r')
    atom_coords = []
    for output_line in gamess_output:
        if "EQUILIBRIUM GEOMETRY LOCATED" in output_line:
            while True:
                for selected_line in gamess_output:
                    if selected_line is not "\n":
                        atom_coords.append(selected_line)
                    else:
                        logging.debug("Extracted atom coordinates from gamess output file.")
                        gamess_output.close()
                        return atom_coords


def read_gamess_header(old_input_name):
    old_input_file = open(old_input_name, 'r')
    header = []
    for header_line in old_input_file:
        if "C1" not in header_line:
            header.append(header_line)
        else:
            header.append(header_line)
            logging.debug("Extracted header from gamess input file.")
            break
    return header


def set_basis_set():
    global selected_basis_set, selected_basis_dict
    if BASIS_SET == "Pople":
        selected_basis_set = Pople.pople_basis_sets
        selected_basis_dict = Pople.pople_basis_dict
    elif BASIS_SET == "Correlation":
        selected_basis_set = Correlation.correlation_basis_sets
        selected_basis_dict = Correlation.correlation_basis_dict
    elif BASIS_SET == "Polarization":
        selected_basis_set = Polarization.polarization_basis_sets
        selected_basis_dict = Polarization.polarization_basis_dict
    else:
        logging.warning("Invalid basis set selected. Terminating process.")
        sys.exit()
