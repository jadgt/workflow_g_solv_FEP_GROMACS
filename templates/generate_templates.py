import os

# Read the contents of the free_energy.mdp file
with open("free_energy.mdp", "r") as f:
    fe_contents = f.read()

# Loop over the list of mdp files and add the free energy parameters
for mdp_file in ["minim.mdp", "nvt.mdp", "npt.mdp", "md.mdp"]:
    # Read the contents of the original mdp file
    with open(mdp_file, "r") as f:
        mdp_contents = f.read()

    # Append the free energy parameters to the end of the file
    new_contents = mdp_contents + fe_contents

    # Write the new contents to a new file with the "_fep" suffix
    with open(mdp_file[:-4] + "_fep.mdp", "w") as f:
        f.write(new_contents)

print("Done!")
