class Correlation:  # CCnWC
    # Processing order for basis sets.
    correlation_basis_sets = ["cc-pwCVDZ", "cc-pwCVTZ", "cc-pwCVQZ"]

    # Parameters for basis sets
    # "Basis set": (GBASIS, NGAUSS, NDFUNC, NPFUNC, DIFFSP, DIFFS)
    correlation_basis_dict = {"cc-pwCVDZ": "CCnWC",
                              "cc-pwCVTZ": "CCnWC",
                              "cc-pwCVQZ": "CCnWC"}
