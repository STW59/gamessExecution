#!/usr/bin/python3
class Pople:
    # Processing order for basis sets.
    pople_basis_sets = ["4-31G",
                        "5-31G",
                        "6-31G",
                        "6-311G",
                        "6-311G(d)",
                        "6-311G(d,p)",
                        "6-311+G(d,p)",
                        "6-311++G(d,p)"]

    # Parameters for basis sets
    # "Basis set": (GBASIS, NGAUSS, NDFUNC, NPFUNC, DIFFSP, DIFFS)
    pople_basis_dict = {"4-31G": ("N31", "4", "", "", "", ""),
                        "5-31G": ("N31", "5", "", "", "", ""),
                        "6-31G": ("N31", "6", "", "", "", ""),
                        "6-311G": ("N311", "5", "", "", "", ""),
                        "6-311G(d)": ("N311", "6", "1", "", "", ""),
                        "6-311G(d,p)": ("N311", "6", "1", "1", "", ""),
                        "6-311+G(d,p)": ("N311", "6", "1", "1", ".TRUE.", ""),
                        "6-311++G(d,p)": ("N311", "6", "1", "1", ".TRUE.", ".TRUE.")}