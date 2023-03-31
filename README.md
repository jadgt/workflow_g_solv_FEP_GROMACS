# Calculating free energy of solvation with the FEP approach in GROMACS

Free energy perturbation (FEP) is a powerful computational technique used to calculate the free energy of solvation of a molecule by simulating the transfer of the molecule from a reference environment to the solvent of interest. FEP is considered to be a highly accurate method for calculating free energies, provided that the simulation is carried out carefully with an appropriate force field and sampling protocol.

Compared to implicit solvent models, FEP is generally considered to be more accurate, as it takes into account the explicit interactions between solvent molecules and the solute. Implicit solvent models, on the other hand, approximate the solvent environment as a continuum, which can lead to inaccuracies in the calculated free energies.

However, implicit solvent models can be computationally less expensive than FEP and may be appropriate in situations where the solvent effects are less important, such as when studying highly hydrophobic molecules or large protein-protein complexes.

Let us consider an example where the solvent is extremely polar as in the case of HCN (hydrogen cyanide) and how can we approach the free energy of solvation of the liquid by means of a FEP method.

The general workflow will be:

1. Preparation of the input files:

    - Create a topology file (.top) for HCN using a suitable force field such as CHARMM, AMBER, or OPLS.
    - Create a coordinate file (.gro) for HCN.
    - Create a topology file and coordinate file for the solvent molecules, such as water (.top and .gro).
2. Solvation of HCN:

    - Generate the solvated structure of HCN by placing the HCN molecule in the center of a cubic box filled with solvent molecules.
    - Energy minimize the system to remove any steric clashes and relieve any unfavorable contacts between the solute and solvent molecules.
3. Preparation of simulation input files:

    - Generate a set of simulation input files for each window of the FEP simulation using the grompp command in GROMACS. Each window represents a different value of the coupling parameter λ, which interpolates between the non-interacting (λ=0) and fully interacting (λ=1) states of HCN with the solvent molecules. The FEP simulations should cover a range of λ values with a small enough interval to ensure a smooth λ-dependence of the free energy.
    - Use the mdrun command to run the simulation for each window using the appropriate settings, such as the number of steps, timestep, thermostat, barostat, etc. It is recommended to use a soft-core potential to avoid singularities when λ=0.
4. Calculation of free energy:

    - Analyze the output files from each FEP simulation using the gmx analyze tool to extract the potential energies, virial, and other relevant parameters.
    - Use the gmx bar tool to perform the BAR (Bennett's acceptance ratio) analysis to calculate the free energy difference between adjacent windows.
    - Use the gmx energy tool to extract the components of the free energy, such as the Lennard-Jones and electrostatic contributions.
5. Post-processing and analysis:

    - Combine the free energy values from all the windows using appropriate techniques such as the thermodynamic integration (TI) or MBAR (multistate Bennett acceptance ratio) to obtain the final free energy of solvation of HCN.
    - Analyze the convergence and error estimates of the calculated free energy values and ensure that the results are statistically significant.

### Full disclaimer: 
**The reliability of the free energy of solvation is highly dependent on the accuracy of the force field, make sure to test the force field before or take the parameters from reliable references where higher level of theory has been used.**

### The force field for HCN

Browsing in the bibliography some good studies have been done for the determination of the force field parameters of HCN. Since we aim to simulate the liquid structure and the free energy of solvation, the bonded parameters will not be very relevant, but the non-bonded.

A good reference is given by the work of Martiniano and Costa Cabral (https://doi.org/10.1016/j.cplett.2012.10.080.). So, we take the non-bonded parameters for that reference to build the force field of the liquid. The force field is contained in the files HCN.itp and topol.top
