from pathlib import Path

def split_xyz_trajectory(input_file, output_dir):
    input_file = Path(input_file)
    output_dir = Path(output_dir) / "Split_Trajectory"
    output_dir.mkdir(parents=True, exist_ok=True)

    step = 1
    with open(input_file, "r") as infile:
        while True:
            atom_count_line = infile.readline()

            if not atom_count_line:
                break

            if not atom_count_line.strip():
                continue

            n_atoms = int(atom_count_line.strip())
            comment_line = infile.readline()
            output_file = output_dir / f"step_{step:03d}.xyz"

            with open(output_file, "w") as outfile:
                outfile.write(atom_count_line)
                outfile.write(comment_line)

                for _ in range(n_atoms):
                    atom_line = infile.readline()
                    if not atom_line:
                        raise ValueError(f"Unexpected end of file while reading step {step}.")
                    outfile.write(atom_line)
            step += 1


def split_lammpstrj_trajectory(input_file, output_dir):
    input_file = Path(input_file)
    output_dir = Path(output_dir) / "Split_Trajectory"
    output_dir.mkdir(parents=True, exist_ok=True)

    step = 0
    outfile = None
    try:
        with open(input_file, "r") as infile:
            for line in infile:
                if line.startswith("ITEM: TIMESTEP"):
                    if outfile is not None:
                        outfile.close()

                    step += 1
                    output_file = output_dir / f"step_{step:03d}.lmpstep"
                    outfile = open(output_file, "w")

                if outfile is not None:
                    outfile.write(line)

        if step == 0:
            raise ValueError("No LAMMPS timesteps found. Expected lines starting with 'ITEM: TIMESTEP'.")

    finally:
        if outfile is not None:
            outfile.close()

def split_trajectory(input_file, output_dir, trajectory_format):
    if trajectory_format == "xyz":
        split_xyz_trajectory(input_file, output_dir)

    elif trajectory_format == "lammpstrj":
        split_lammpstrj_trajectory(input_file, output_dir)

    else:
        raise ValueError("trajectory_format must be 'xyz' or 'lammpstrj'.")
