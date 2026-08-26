import numpy as np

def lmpstep_to_xyz(input_file, output_file, type_map=None, coordinate_mode="auto"):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Parse the LAMMPS dump format
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('ITEM: TIMESTEP'):
            timestep = int(lines[i+1].strip())
            i += 2
        elif line.startswith('ITEM: NUMBER OF ATOMS'):
            n_atoms = int(lines[i+1].strip())
            i += 2
        elif line.startswith('ITEM: BOX BOUNDS'):
            # Parse box bounds - could be in different formats
            box_bounds_line = line
            tilt = 'xy xz yz' in box_bounds_line
            
            # Read the three box bound lines
            x_bounds = lines[i].strip().split()
            y_bounds = lines[i+1].strip().split()
            z_bounds = lines[i+2].strip().split()
            i += 3
            
            # Parse bounds
            xlo = float(x_bounds[0])
            xhi = float(x_bounds[1])
            ylo = float(y_bounds[0])
            yhi = float(y_bounds[1])
            zlo = float(z_bounds[0])
            zhi = float(z_bounds[1])
            
            # If tilt is present, there are extra values
            if tilt and len(x_bounds) > 2:
                xy = float(x_bounds[2])
                xz = float(y_bounds[2]) if len(y_bounds) > 2 else 0.0
                yz = float(z_bounds[2]) if len(z_bounds) > 2 else 0.0
            
            box = [[xlo, xhi], [ylo, yhi], [zlo, zhi]]
            
        elif line.startswith('ITEM: ATOMS'):
            # Parse atom data
            atom_labels = line.split()[2:]  # Get column names
            i += 1
            
            # Read atom data
            atom_lines = lines[i:i+n_atoms]
            i += n_atoms
            
            # Parse atom data
            atoms = []
            for atom_line in atom_lines:
                values = atom_line.strip().split()
                atom_dict = dict(zip(atom_labels, values))
                
                # Convert values to appropriate types
                atom_type = int(float(atom_dict.get('type', atom_dict.get('atom-type', 0))))
                x = float(atom_dict.get('x', 0.0))
                y = float(atom_dict.get('y', 0.0))
                z = float(atom_dict.get('z', 0.0))
                
                # Handle scaled coordinates if needed
                if coordinate_mode == "scaled" or (coordinate_mode == "auto" and 
                    all(0 <= float(v) <= 1 for v in [x, y, z])):
                    # Convert scaled to Cartesian
                    x = xlo + x * (xhi - xlo)
                    y = ylo + y * (yhi - ylo)
                    z = zlo + z * (zhi - zlo)
                
                # Get element symbol from type_map
                if type_map and atom_type in type_map:
                    element = type_map[atom_type]
                else:
                    element = f"X{atom_type}" 
                atoms.append((element, x, y, z))
            
            # Write XYZ file
            with open(output_file, 'w') as f_out:
                f_out.write(f"{len(atoms)}\n")
                f_out.write(f"Timestep: {timestep}\n")
                for element, x, y, z in atoms:
                    f_out.write(f"{element} {x:.8f} {y:.8f} {z:.8f}\n")
            return  

    raise ValueError(f"Could not parse LAMMPS dump file: {input_file}")
