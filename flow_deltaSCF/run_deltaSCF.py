#!/usr/bin/env python
import sys
import os
import abipy.abilab as abilab
import abipy.flowtk as flowtk
import abipy.data as abidata
from abipy.core import structure

def get_non_eq_sites(structure,replaced_atom):
    ### return a list of positions of non-equivalent sites for the replaced atom. ###
    irred=structure.spget_equivalent_atoms().eqmap # mapping from inequivalent sites to atoms sites
    positions=structure.get_symbol2indices()[replaced_atom] # get indices of the replaced atom
    
    index_different_sites=[]

    for i in positions:
        if len(irred[i]) != 0:
            index_different_sites.append(irred[i][0])
            
    return(index_different_sites)

def make_doped_supercell(prim_structure,supercell_size,replaced_atom,dopant_atom):
    #return a list of doped supercell structure, one for each non-equivalent site of the replaced atom
    my_structure=prim_structure.copy()
    my_structure.make_supercell(supercell_size)
    list_ineq_pos=get_non_eq_sites(my_structure,replaced_atom)
    
    doped_structure_list=[]
    
    for pos in list_ineq_pos:
        final_structure=my_structure.copy()    
        final_structure.replace(pos,dopant_atom)  
        doped_structure_list.append(final_structure)
    
    return doped_structure_list    


def scf_inp(structure):
    pseudodir='/home/ucl/modl/jbouq/psps_paw_pbe/'
    
    pseudos = ('Eu.GGA_PBE-JTH.xml',
               'Sr.GGA_PBE-JTH.xml',
               'Al.GGA_PBE-JTH.xml',
               'Li.GGA_PBE-JTH.xml',
               'O.GGA_PBE-JTH.xml',
               'N.GGA_PBE-JTH.xml')
    gs_scf_inp = abilab.AbinitInput(structure=structure, pseudos=pseudos,pseudo_dir=pseudodir)
    gs_scf_inp.set_vars(ecut=15,
                        pawecutdg=30,
                        chksymbreak=0,
                        diemac=5,
                        prtwf=-1,
                        nstep=100,
                        toldfe=1e-8,
                        chkprim=0,
                        )

    # Set DFT+U and spinat parameters according to chemical symbols.
    symb2spinat = {"Eu": [0, 0, 7]}
    symb2luj = {"Eu": {"lpawu": 3, "upawu": 7, "jpawu": 0.7}}

    gs_scf_inp.set_usepawu(usepawu=1, symb2luj=symb2luj)
    gs_scf_inp.set_spinat_from_symbols(symb2spinat, default=(0, 0, 0))

    n_val = gs_scf_inp.num_valence_electrons
    n_cond = round(21)

    spin_up_gs = f"\n{int((n_val - 7) / 2)}*1 7*1 {n_cond}*0"
    spin_up_ex = f"\n{int((n_val - 7) / 2)}*1 6*1 0 1 {n_cond - 1}*0" 
    spin_dn = f"\n{int((n_val - 7) / 2)}*1 7*0 {n_cond}*0"

    nsppol = 2
    shiftk = [0.5, 0.5, 0.5]
    ngkpt = [2, 2, 2]

    # Build SCF input for the ground state configuration.
    gs_scf_inp.set_kmesh_nband_and_occ(ngkpt, shiftk, nsppol, [spin_up_gs, spin_dn])
    # Build SCF input for the excited configuration.
    exc_scf_inp = gs_scf_inp.deepcopy()
    exc_scf_inp.set_kmesh_nband_and_occ(ngkpt, shiftk, nsppol, [spin_up_ex, spin_dn])

    return gs_scf_inp,exc_scf_inp


def relax_kwargs():

    # Dictionary with input variables to be added for performing structural relaxations.
    relax_kwargs = dict(
        ecutsm=0.5,
        toldff=1e-5, # TOO HIGH, just for testing purposes.
        tolmxf=1e-4, # TOO HIGH, just for testing purposes.
        ionmov=22,
        dilatmx=1.05,  # Keep this also for optcell 0 else relaxation goes bananas due to low ecut.
        chkdilatmx=0,
    )

    relax_kwargs_gs=relax_kwargs.copy()
    relax_kwargs_gs['optcell']=2 # in the ground state, allow relaxation of the cell 

    relax_kwargs_ex=relax_kwargs.copy()
    relax_kwargs_ex['optcell']=0 # in the excited state, no relaxation of the cell

    return relax_kwargs_gs, relax_kwargs_ex


def build_flow(options):

    # Working directory (default is the name of the script with '.py' removed and "run_" replaced by "flow_")
    if not options.workdir:
        options.workdir = os.path.basename(sys.argv[0]).replace(".py", "").replace("run_", "flow_")

    flow = flowtk.Flow(options.workdir, manager=options.manager)

    #Construct the structures
    prim_structure=structure.Structure.from_file('../SALON_prim.cif')
    structure_list=make_doped_supercell(prim_structure,[1,1,4],'Sr','Eu')

    ####### Delta SCF part of the flow #######
    
    from abipy.flowtk.lumi_works import LumiWork
    
    for stru in structure_list:
       gs_scf_inp, exc_scf_inp = scf_inp(stru)
       relax_kwargs_gs, relax_kwargs_ex = relax_kwargs()
       Lumi_work=LumiWork.from_scf_inputs(gs_scf_inp, exc_scf_inp, relax_kwargs_gs, relax_kwargs_ex,ndivsm=0)
       flow.register_work(Lumi_work)
 
    return flow


@flowtk.flow_main

def main(options):
    """
    This is our main function that will be invoked by the script.
    flow_main is a decorator implementing the command line interface.
    Command line args are stored in `options`.
    """
    return build_flow(options)


if __name__ == '__main__':
    sys.exit(main())


