import os
import shutil

# Path to the folder where the lambda folders will be created
root_dir = '../'

# Number of lambdas
num_lambdas = int(input('Enter the number of lambdas: '))

# Create the lambda directories and their subdirectories for each simulation type
for i in range(num_lambdas):
    lambda_dir = os.path.join(root_dir, 'lambda_{}'.format(i))
    os.makedirs(lambda_dir)
    for sim_type in ['EM', 'NVT', 'NPT', 'MD']:
        sim_dir = os.path.join(lambda_dir, sim_type)
        os.makedirs(sim_dir)

# Copy the .mdp files for each simulation type to their respective directories in each lambda folder
mdp_files = ['minim_fep.mdp', 'nvt_fep.mdp', 'npt_fep.mdp', 'md_fep.mdp']
for i in range(num_lambdas):
    lambda_dir = os.path.join(root_dir, 'lambda_{}'.format(i))
    for j, sim_type in enumerate(['EM', 'NVT', 'NPT', 'MD']):
        src_mdp_file = mdp_files[j]
        dst_mdp_file = src_mdp_file
        dst_mdp_path = os.path.join(lambda_dir, sim_type, dst_mdp_file)
        shutil.copy(src_mdp_file, dst_mdp_path)

        # Modify the init_lambda_state value in the copied .mdp files
        with open(dst_mdp_path, 'r') as f:
            contents = f.readlines()
        for k, line in enumerate(contents):
            if 'init_lambda_state' in line:
                contents[k] = 'init_lambda_state        = {}\n'.format(i)
                break
        with open(dst_mdp_path, 'w') as f:
            f.writelines(contents)



