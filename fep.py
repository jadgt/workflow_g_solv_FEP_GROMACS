### GROMACS FEP Automatic Routine
# Created by Juan de Gracia
# System preparation routine

import os
import shutil

# define the function to write mdp files
def write_mdp(mdp_string, mdp_name, directory):
    mdp_filename=os.path.join(directory,mdp_name)
    mdp_filehandle=open(mdp_filename,'w')
    mdp_filehandle.write(mdp_string)
    mdp_filehandle.close() 

# get the path to the working directory
pwd = os.getcwd()

# path to input and output files
input_files = os.path.join(pwd, 'input_files')
output_files = os.path.join(pwd, 'output_files')

# create output_files directory if it doesn't exist
if not os.path.isdir(output_files):
    os.mkdir(output_files)

# Ask for the filenames
print("""
AUTOMATIC FREE ENERGY OF SOLVATION ROUTINE
------------------------------------------
System preparation subroutine
------------------------------------------
Input the file names (including the extension) that shall be used along the simulation.
If you are using a custom solvent with a topology (.itp) associated, introduce the file name with extension
otherwise, leave it blank
""")
gro_file_name = input("Enter the name of the .gro file: ")
top_file_name = input("Enter the name of the .top file: ")
solute_itp_name = input("Enter the name of the solute .itp file: ")
solvent_itp_name = input("Enter the name of the solvent .itp file: ")

# Only add the solvent_itp_name to file_names if it is not empty
file_names = [gro_file_name, top_file_name, solute_itp_name]
if solvent_itp_name.strip():
    file_names.append(solvent_itp_name)

# copy selected files from input_files directory to output_files directory
for file_name in file_names:
    shutil.copy(os.path.join(input_files, file_name.strip()), os.path.join(output_files, file_name.strip()))

# define energy minimization mdp options as a separate file
em_mdp = """
; minimal mdp options for energy minimization
integrator               = steep
nsteps                   = 500
coulombtype              = pme
"""

# write energy minimization mdp file
write_mdp(em_mdp, 'em.mdp', output_files)

# execute energy minimization simulation
os.chdir(output_files)
os.system(f'gmx grompp -f em.mdp -c {gro_file_name} -o em.tpr')
os.system('gmx mdrun -v -deffnm em')

# define equilibration mdp options as a separate file
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

# write equilibration mdp file
write_mdp(equil_mdp, 'equil.mdp', output_files)

# execute equilibration simulation
os.system('gmx grompp -f equil.mdp -c em.gro -o equil.tpr')
os.system('gmx mdrun -ntmpi 1 -deffnm equil') # -ntmpi 1 is defined since the system is quite small

### GROMACS FEP Automatic Routine
# Running FEP routine
print("""
AUTOMATIC FREE ENERGY OF SOLVATION ROUTINE
------------------------------------------
FEP Simulation subroutine
------------------------------------------
Example of usage:
Enter the number of lambdas: 7
Enter the set of fep-lambdas (separated by space): 0.0 0.2 0.4 0.6 0.8 0.9 1.0
""")
# Ask for the number of lambdas
number_of_lambdas = int(input("Enter the number of lambdas: "))

# Ask for the fep-lambdas values
fep_lambdas_input = input("Enter the set of fep-lambdas (separated by space): ")
fep_lambdas = fep_lambdas_input.split()

# define FEP mdp options as a separate file
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
couple-moltype           = HCN
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
# Create a lambda file for every lambda step, copy files and run
for lambda_number in range(number_of_lambdas):
    lambda_directory = os.path.join(output_files, f"lambda_{lambda_number:0>2}")
    os.mkdir(lambda_directory)
    gro_file = os.path.join(output_files, 'equil.gro')
    top_file = os.path.join(output_files, top_file_name)
    itp_solute = os.path.join(output_files, solute_itp_name)
    shutil.copy(gro_file, os.path.join(lambda_directory, 'conf.gro'))
    shutil.copy(top_file, lambda_directory)
    shutil.copy(itp_solute, lambda_directory)
    # Only copy the solvent itp if it was given
    if solvent_itp_name.strip():
        itp_solvent = os.path.join(output_files, solvent_itp_name)
        shutil.copy(itp_solvent, lambda_directory)
    write_mdp(run_mdp.format(lambda_number, ' '.join(fep_lambdas)), 'grompp.mdp', lambda_directory)
    os.chdir(lambda_directory)
    os.system('gmx grompp')
    os.system('gmx -ntmpi 2 mdrun')

#Analysis of the FEP output and computing the Free Energy

bar_string = ''
for lambda_number in range(number_of_lambdas):
    lambda_directory = os.path.join(output_files, 'lambda_{:0>2}'.format(lambda_number))
    bar_string = bar_string + lambda_directory + '/dhdl.xvg '

command = 'gmx bar -b 100 -f ' + bar_string
os.system(command)