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

A good reference is given by the work of Martiniano and Costa Cabral (https://doi.org/10.1016/j.cplett.2012.10.080.). So, we take the non-bonded parameters for that reference to build the force field of the liquid. The force field is contained in the files [itp file](HCN.itp) and [top file](topol.top)

The easy part is to get a [geometry of HCN](HCN.gro).

### Solvation box

The next thing we need to do is create a solvation box and introduce as many molecules as the density required.
In this case, one can build a simple cubic box using the command:
```
gmx editconf -f HCN -c -d 1.0 -bt cubic -o box
```
With this command we can create a cubic box that goes 1 nm away from the molecule in x,y and z.

Then we solvate with the command:
```
gmx insert-molecules -f box -ci HCN -nmol 173 -o liq
```
The number 173 comes from the density at 278 K (0.704 g/cm3) and the molar weight of HCN and the volume of the box.

Once we have the solvated box we can run an MD simulation to test if the parameters works fine. (I let this evaluation to the expertise of the reader but generally is good practice to check with experimental values.)

### Preparing the FEP files

Once we have all the files ready and we are satisfied with the Force Field, we can prepare for the FEP simulations. 
First thing, in order to make the FEP possible, since we are simulating the pure liquid conditions we need to create a ficticious residue (which is exactly the same as one HCN molecule) so the program will identify the single HCN molecule for which we want to calculate the free energy of solvation. 

For that matter, I have created a second residue called [UNK](UNK.gro) and added to the topology as seen in the [top file](topol.top). Also, I have used the molecule [HCN](HCN.gro) as the central molecule, built the periodic box as before and solvated with the UNK.gro file as follows:
```
gmx insert-molecules -f box -ci UNK -nmol 173 -o liq
```
That produces the file contained in this tutorial [liq.gro](liq.gro)

Once we have everything ready, we come to the trickiest part, building the FEP files. For making this easy we will use an auxiliary file contained in the folder [templates](/templates/) called [free_energy.mdp](/templates/free_energy.mdp).
Let us examine that file:
```
; Free energy control parameters
free_energy              = yes
couple-moltype           = HCN  ; name of moleculetype to decouple
init_lambda_state        = 0
delta_lambda             = 0
calc_lambda_neighbors    = 1
couple-lambda0           = vdw-q
couple-lambda1           = none
couple-intramol          = yes
; Vectors of lambda specified here
; lambdas                  0    1    2    3    4    5    6    7    8    9    10
vdw_lambdas              = 0.00 0.10 0.20 0.30 0.40 0.50 0.60 0.70 0.80 0.90 1.00
coul_lambdas             = 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
bonded_lambdas           = 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
restraint_lambdas        = 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
; Masses are not changing (particle identities are the same at lambda = 0 and lambda = 1)
mass_lambdas             = 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
; Not doing simulated temperting here
temperature_lambdas      = 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
; Options for the decoupling
sc-alpha                 = 0.5
sc-coul                  = no       ; linear interpolation of Coulomb (none in this case)
sc-power                 = 1
sc-sigma                 = 0.3
nstdhdl                  = 10
disre           = simple
nstdisreout     = 0
```
Here we have defined 10 lambdas and we are changing the vdw parameters only. A couple of things are really important:
1. The molecule to decouple: This is why we needed to define an additional residue name in order to make the program understand what is the solute (HCN) and what is the solvent (UNK)
```
couple-moltype           = HCN  ; name of moleculetype to decouple
```
2. The non bonded interactions to be decoupled: In the beginning we want the vdW and Coulomb forces to be present, but by the end it should be gone since we are moving from solvent to vaccum.
```
couple-lambda0           = vdw-q
couple-lambda1           = none
```
3. Only the lambdas for vdW will change, not the Coulombs: This is a requirement from the program, otherwise it will print a warning.
```
; lambdas                  0    1    2    3    4    5    6    7    8    9    10
vdw_lambdas              = 0.00 0.10 0.20 0.30 0.40 0.50 0.60 0.70 0.80 0.90 1.00
coul_lambdas             = 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
```
Once the `free_energy.mdp` is ready, we can modify the exact same mdp files we have used for our MD test simulation (`minim.mdp,nvt.mdp,npt.mdp and md.mdp`) with the free energy perturbation control instructions contained in `free_energy.mdp` by simply executing the script [generate_templates.py](/templates/generate_templates.py) inside the templates folder.

```
python generate_templates.py
```
This will create 4 new mdp files with the suffix `_fep.mdp`. You can have a look in the folder [templates](/templates/).

### Preparing all the simulations

Once we have our files ready, in the folder [templates](/templates/) can be found a python script called [generate_fep.py](/templates/generate_fep.py) that will take care of creating the Lambda folders and putting the corresponding mdp files inside while changing for every mdp file the line
```
init_lambda_state        = 0
```
to the corresponding lambda state. For example, in lambda 5 it should appear:
```
init_lambda_state        = 5
```
**The code will ask you to input the number of lambdas to be calculated, you have to input 10 + 1 = 11 (remember that lambdas starts with 0**

### Running the FEP simulation

Now, is time to run the FEP simulation that require executing every simulation in an ordered manner and using the last geometry as the starting one for the next. More specifically, the order is:
1. Lambda_0
    1.1 EM
    1.2 NVT
    1.3 NPT 
    1.4 MD
2. Lambda_1
....
11. Lambda_10
    11.1 EM
    11.2 NVT
    11.3 NPT 
    11.4 MD 

Manually it could be a really tedious task, but in the folder templates there is a bash script called [FEP.sh](/templates/FEP.sh) that will take care of it for you.

The code will ask you to input the number of lambdas to be calculated, we use 11 as for the previous step.
The code will ask you also to input the working directory which is the one where all the lambda folders have been copied or the parent folder of templates. So, prior to execute the script type:
```
pwd
```
And copy and paste the path that is printed.

Now is just time to wait for the results :).