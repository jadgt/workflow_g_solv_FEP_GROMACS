#!/bin/bash

# Prompt the user to input the number of lambdas to run
read -p "Enter the number of lambdas to run: " num_lambdas

# Prompt the user to input the root directory
read -p "Enter the path to the root directory: " root_dir

# Loop over the lambda folders and run the simulations in order
for i in $(seq 0 $(($num_lambdas - 1))); do
    lambda_dir="$root_dir/lambda_$i"
    for sim_type in EM NVT NPT MD; do
        sim_dir="$lambda_dir/$sim_type"
        
        # Run the simulation
        cd "$sim_dir"
        if [ "$sim_type" == "EM" ]; then
            gmx grompp -f minim_fep.mdp -c "$root_dir"/liq.gro -p "$root_dir"/topol.top -o em.tpr
            gmx mdrun -v -deffnm em
        elif [ "$sim_type" == "NVT" ]; then
            gmx grompp -f nvt_fep.mdp -c "$root_dir"/lambda_$(($i))/EM/em.gro -p "$root_dir"/topol.top -o nvt.tpr
            gmx mdrun -v -deffnm nvt
        elif [ "$sim_type" == "NPT" ]; then
            gmx grompp -f npt_fep.mdp -c "$root_dir"/lambda_$(($i))/NVT/nvt.gro -p "$root_dir"/topol.top -o npt.tpr
            gmx mdrun -v -deffnm npt
        else
            gmx grompp -f md_fep.mdp -c "$root_dir"/lambda_$(($i))/NPT/npt.gro -p "$root_dir"/topol.top -o md.tpr
            gmx mdrun -v -deffnm md
        fi
        
        # Check if simulation completed successfully
        if [ ! -f "$sim_type".gro ]; then
            echo "Simulation failed! Check for errors in $sim_dir"
            exit 1
        fi
        
        # Copy the output file to the next lambda folder
        if [ "$sim_type" == "MD" ] && [ $i -lt $(($num_lambdas - 1)) ]; then
            cp md.gro "$root_dir"/lambda_$(($i + 1))/EM/
        fi

    done


    echo "Finished lambda $i"
done
