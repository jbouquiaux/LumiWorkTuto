#!/usr/bin/env python

import sys
import os
import numpy as np
import abipy.abilab as abilab
import abipy.data as data
import abipy.flowtk as flowtk
from abipy.core import Structure

def make_input(structure):
    pseudodir='/SCRATCH/acad/leds/jbouq/psps_paw_pbe'
    pseudos = ('Sr.GGA_PBE-JTH.xml',
               'Al.GGA_PBE-JTH.xml',
               'Li.GGA_PBE-JTH.xml',
               'O.GGA_PBE-JTH.xml',
               'N.GGA_PBE-JTH.xml')
    # Initialize the input

    gs_inp = abilab.AbinitInput(structure=structure, pseudos=pseudos,pseudo_dir=pseudodir)
    
    gs_inp.set_vars(
	chkprim=0,
	nstep=200,
        ecut=10,
        pawecutdg=20,
	pawxcdev=0, # important for dfpt with paw
        ngkpt=[1, 1, 1],
        nshiftk=1,
        shiftk=[ 0,  0,  0],
        tolvrs=1.0e-25,
        diemac=3.0,
    )

    return gs_inp

def build_flow(options):
    # Working directory (default is the name of the script with '.py' removed and "run_" replaced by "flow_")
    if not options.workdir:
        options.workdir = os.path.basename(sys.argv[0]).replace(".py", "").replace("run_", "flow_")

                            
    stru=Structure.from_file("SALON_prim.cif")
    stru.make_supercell([1,1,4])
    scf_input=make_input(stru)
    flow = flowtk.PhononFlow.from_scf_input(options.workdir, scf_input,
                                            ph_ngqpt=(1, 1, 1), with_becs=False)


    return flow


@flowtk.flow_main
def main(options):
    """
    This is our main function that will be invoked by the script.
    flow_main is a decorator implementing the command line interface.
    Command line args are stored in `options`.
    """
    return build_flow(options)


if __name__ == "__main__":
    sys.exit(main())
