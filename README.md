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

A good reference is given by the work of Martiniano and Costa Cabral (https://doi.org/10.1016/j.cplett.2012.10.080.). So, we take the non-bonded parameters for that reference to build the force field of the liquid. The force field is contained in the files [itp file](/input_files/HCN.itp) and [top file](/input_files/topol.top)

The easy part is to get a [geometry of HCN](/input_files/HCN.gro).

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

### System preparation routine and FEP simulation automatized!

Once we have all the files ready and we are satisfied with the Force Field, we can prepare for the FEP simulations. 
First thing, in order to make the FEP possible, since we are simulating the pure liquid conditions we need to create a ficticious residue (which is exactly the same as one HCN molecule) so the program will identify the single HCN molecule for which we want to calculate the free energy of solvation. 

For that matter, I have created a second residue called [UNK](/input_files/UNK.itp) and added to the topology as seen in the [top file](/input_files/topol.top). Also, I have used the molecule [HCN](/input_files/HCN.gro) as the central molecule, built the periodic box as before and solvated with the [UNK geometry](/input_files/UNK.gro) file as follows:
```
gmx insert-molecules -f box -ci UNK -nmol 173 -o liq
```
That produces the file contained in this tutorial [liq.gro](/input_files/liq.gro)

Once we have everything ready, we can start working on the scripts that automatically will perform our FEP simulation. Let us start having a look to the script [fep.py](fep.py). In that script the configuration files are defined as variables that will be used for minimizing and equilibrating the system.

So, in this case, I will use the minimum configuration options needed and the user of this tutorial can introduce as many modifications as desired.
**Energy minimization**
```
em_mdp = """
; minimal mdp options for energy minimization
integrator               = steep
nsteps                   = 500
coulombtype              = pme
"""
```
**NPT equilibration**
```
equil_mdp = """
; equilibration mdp options
integrator               = md
nsteps                   = 100000
dt                       = 0.002
nstenergy                = 100
rlist                    = 1.1
nstlist                  = 10
rvdw                     = 1.1
coulombtype              = pme
rcoulomb                 = 1.1
fourierspacing           = 0.13
constraints              = h-bonds
tcoupl                   = v-rescale
tc-grps                  = system
tau-t                    = 0.5
ref-t                    = 278
pcoupl                   = C-rescale
ref-p                    = 1
compressibility          = 4.5e-5
tau-p                    = 1
gen-vel                  = yes
gen-temp                 = 278
"""
```
*Notice that the temperature I am using in this case is 278 K, but the user can change this at will.*

Once we are satisfied with the options for minimization and equilibration we can have a look at the FEP simulation configuration file
```
run_mdp = """
; We'll use the sd integrator (an accurate and efficient leap-frog stochastic dynamics integrator) with 100000 time steps (200ps)
integrator               = sd
nsteps                   = 100000
dt                       = 0.002
nstenergy                = 1000
nstcalcenergy            = 50 ; should be a divisor of nstdhdl 
nstlog                   = 5000
; Cut-offs at 1.0nm
rlist                    = 1.1
rvdw                     = 1.1
; Coulomb interactions
coulombtype              = pme
rcoulomb                 = 1.1
fourierspacing           = 0.13
; Constraints
constraints              = h-bonds
; Set temperature to 300K
tc-grps                  = system
tau-t                    = 2.0
ref-t                    = 278
; Set pressure to 1 bar with a thermostat that gives a correct
; thermodynamic ensemble
pcoupl                   = C-rescale
ref-p                    = 1.0
compressibility          = 4.5e-5
tau-p                    = 5.0

; Set the free energy parameters
free-energy              = yes
couple-moltype           = HCN ; Insert here the name of the solute residue, in our case is called HCN !!
nstdhdl                  = 50 ; frequency for writing energy difference in dhdl.xvg, 0 means no ouput, should be a multiple of nstcalcenergy. 
; These 'soft-core' parameters make sure we never get overlapping
; charges as lambda goes to 0
; Soft-core function
sc-power                 = 1
sc-sigma                 = 0.3
sc-alpha                 = 1.0
; We still want the molecule to interact with itself at lambda=0
couple-intramol          = no
couple-lambda1           = vdwq
couple-lambda0           = none
init-lambda-state        = {}

; These are the lambda states at which we simulate
; For separate LJ and Coulomb decoupling, use
fep-lambdas              = {}
"""
```
Once we are satisfied, we can execute the script typing in terminal:
```
python fep.py
```
And the script will ask as arguments the name of the files that shall be included in the simulation by extension:
```
Enter the name of the .gro file: liq.gro
Enter the name of the .top file: topol.top
Enter the name of the solute .itp file: HCN.itp
Enter the name of the solvent .itp file: UNK.itp
```
After the equilibration is completed, the script will ask to input the number of lambdas that we want to use and the numbers for the lambdas, as follows:

```
Enter the number of lambdas: 5
Enter the set of fep-lambdas (separated by space): 0.0 0.5 0.7 0.9 1.0
```
I have picked more density towards the decoupling for being the most sensitive part.

Once inputed that, the script will take care of the whole calculation and display the final results in terminal.

Enjoy!