import numpy as np

def lmpstep_to_xyz(input_file, output_file, type_map=None, coordinate_mode="auto"):
    with open(input_file, 'r') as f:
        lines = f.readlines()
        
    i = 0
    timestep = 0
    n_atoms = 0
    box = None
    atom_labels = []
    atom_data_start = -1
    
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
            
            box = [[xlo, xhi], [ylo, yhi], [zlo, zhi]]
            
        elif line.startswith('ITEM: ATOMS'):
            # Parse atom data
            atom_labels = line.split()[2:]  # Get column names 
            i += 1
            atom_data_start = i
            break  
        else:
            i += 1
    
    if atom_data_start == -1:
        raise ValueError(f"Could not find ITEM: ATOMS in file: {input_file}")
    
    # Read atom data
    atom_lines = lines[atom_data_start:atom_data_start + n_atoms]
    
    if len(atom_lines) < n_atoms:
        raise ValueError(f"Expected {n_atoms} atoms but found {len(atom_lines)} in {input_file}")
    
    # Parse atom data
    atoms = []
    for atom_line in atom_lines:
        values = atom_line.strip().split()
        if not values:
            continue
            
        atom_dict = dict(zip(atom_labels, values))
        atom_type = None
        for key in ['type', 'atom-type', 'element']:
            if key in atom_dict:
                try:
                    atom_type = int(float(atom_dict[key]))
                    break
                except ValueError:
                    continue
        
        if atom_type is None:
            raise ValueError(f"Could not find atom type in line: {atom_line}")
        
        try:
            x = float(atom_dict.get('x', 0.0))
            y = float(atom_dict.get('y', 0.0))
            z = float(atom_dict.get('z', 0.0))
        except (ValueError, KeyError) as e:
            raise ValueError(f"Could not parse coordinates in line: {atom_line}")
        
        if coordinate_mode == "scaled" or (coordinate_mode == "auto" and 
            all(0 <= float(v) <= 1 for v in [x, y, z])):
            # Convert scaled to Cartesian
            if box is None:
                raise ValueError("Box bounds not found for scaled coordinates")
            x = box[0][0] + x * (box[0][1] - box[0][0])
            y = box[1][0] + y * (box[1][1] - box[1][0])
            z = box[2][0] + z * (box[2][1] - box[2][0])
        
        # Get element symbol from type_map
        if type_map and atom_type in type_map:
            element = type_map[atom_type]
        
        atoms.append((element, x, y, z))
    
    with open(output_file, 'w') as f_out:
        f_out.write(f"{len(atoms)}\n")
        f_out.write(f"Timestep: {timestep}\n")
        for element, x, y, z in atoms:
            f_out.write(f"{element} {x:.8f} {y:.8f} {z:.8f}\n")
