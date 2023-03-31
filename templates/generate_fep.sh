#!/bin/bash

# Path to the folder where the lambda folders will be created
root_dir='../'

# Number of lambdas
read -p "Enter the number of lambdas: " num_lambdas

# Create the lambda directories and their subdirectories for each simulation type
for ((i=0; i<num_lambdas; i++)); do
    lambda_dir="$root_dir/lambda_$i"
    mkdir -p "$lambda_dir"
    for sim_type in "EM" "NVT" "NPT" "MD"; do
        sim_dir="$lambda_dir/$sim_type"
        mkdir -p "$sim_dir"
    done
done

# Copy the .mdp files for each simulation type to their respective directories in each lambda folder
mdp_files=("minim_fep.mdp" "nvt_fep.mdp" "npt_fep.mdp" "md_fep.mdp")
sim_types=("EM" "NVT" "NPT" "MD")
for ((i=0; i<num_lambdas; i++)); do
    lambda_dir="$root_dir/lambda_$i"
    for ((j=0; j<${#mdp_files[@]}; j++)); do
        src_mdp_file="${mdp_files[j]}"
        sim_type="${sim_types[j]}"
        dst_mdp_file="${src_mdp_file}"
        dst_mdp_path="$lambda_dir/$sim_type/$dst_mdp_file"
        cp "$src_mdp_file" "$dst_mdp_path"

        # Modify the init_lambda_state value in the copied .mdp files
        sed -i "s|init_lambda_state        = 0|init_lambda_state        = $i|" "$dst_mdp_file"
    done
done







