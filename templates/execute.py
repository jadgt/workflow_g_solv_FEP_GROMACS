import os
import subprocess

# Define the root directory where the files are located
root_dir = '/Users/trivino/Desktop/HCN/hcn_liquid'

# Read the number of lambdas from the free_energy.mdp file
num_lambdas = 11

# Loop over the lambda folders and run the simulations in order
for i in range(num_lambdas):
    lambda_dir = os.path.join(root_dir, 'lambda_{}'.format(i))
    for sim_type in ['EM', 'NVT', 'NPT', 'MD']:
        sim_dir = os.path.join(lambda_dir, sim_type)

        # Run the simulation in the simulation directory
        os.chdir(sim_dir)
        if sim_type == 'EM':
            subprocess.run(['gmx', 'grompp', '-f', os.path.join(root_dir, 'minim_fep.mdp'), '-c', os.path.join(root_dir, 'liq.gro'), '-p', os.path.join(root_dir, 'topol.top'), '-o', 'em.tpr'], check=True)
            subprocess.run(['gmx', 'mdrun', '-v', '-deffnm', 'em'], check=True)
        elif sim_type == 'NVT':
            subprocess.run(['gmx', 'grompp', '-f', os.path.join(root_dir, 'nvt_fep.mdp'), '-c', os.path.join(lambda_dir, 'EM', 'em.gro'), '-p', os.path.join(root_dir, 'topol.top'), '-o', 'nvt.tpr'], check=True)
            subprocess.run(['gmx', 'mdrun', '-v', '-deffnm', 'nvt'], check=True)
        elif sim_type == 'NPT':
            subprocess.run(['gmx', 'grompp', '-f', os.path.join(root_dir, 'npt_fep.mdp'), '-c', os.path.join(lambda_dir, 'NVT', 'nvt.gro'), '-p', os.path.join(root_dir, 'topol.top'), '-o', 'npt.tpr'], check=True)
            subprocess.run(['gmx', 'mdrun', '-v', '-deffnm', 'npt'], check=True)
        elif sim_type == 'MD':
            subprocess.run(['gmx', 'grompp', '-f', os.path.join(root_dir, 'md_fep.mdp'), '-c', os.path.join(lambda_dir, 'NPT', 'npt.gro'), '-p', os.path.join(root_dir, 'topol.top'), '-o', 'md.tpr'], check=True)
            subprocess.run(['gmx', 'mdrun', '-v', '-deffnm', 'md'], check=True)

    print('Finished lambda {}'.format(i))
