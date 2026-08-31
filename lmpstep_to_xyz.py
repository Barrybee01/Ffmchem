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
            box_bounds_line = line
            tilt = 'xy xz yz' in box_bounds_line
            i += 1 #I forgot to add this, check here for debugging the ITEM float error
            
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

            if tilt: # grab tilt factors
                xy = float(x_bounds[2]) 
                xz = float(y_bounds[2]) 
                yz = float(z_bounds[2])
            
            box = [[xlo, xhi], [ylo, yhi], [zlo, zhi], [xy, xz, yz]]
            
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

        if all(coord in atom_dict for coord in ['xs', 'ys', 'zs']): 
            coordinate_columns = ['xs', 'ys', 'zs'] 
            file_coordinate_mode = "scaled" 
        elif all(coord in atom_dict for coord in ['x', 'y', 'z']): 
            coordinate_columns = ['x', 'y', 'z'] 
            file_coordinate_mode = "cartesian" 
        else: raise ValueError( f"Could not find coordinates in line: {atom_line}" )
        
        try:
            x = float(atom_dict[coordinate_columns[0]])  
            y = float(atom_dict[coordinate_columns[1]]) 
            z = float(atom_dict[coordinate_columns[2]]) 
        except (ValueError, KeyError) as e:
            raise ValueError(f"Could not parse coordinates in line: {atom_line}")
        
        if file_coordinate_mode == "scaled":
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
        if box is not None: 
            x_length = box[0][1] - box[0][0] 
            y_length = box[1][1] - box[1][0] 
            z_length = box[2][1] - box[2][0] 
            xy = box[3][0] 
            xz = box[3][1] 
            yz = box[3][2] 
            f_out.write( f"{x_length:.8f} {y_length:.8f} {z_length:.8f} " f"{xy:.8f} {xz:.8f} {yz:.8f}\n" ) 
        else: f_out.write(f"Timestep: {timestep}\n") 
            
        for element, x, y, z in atoms:
            f_out.write(f"{element} {x:.8f} {y:.8f} {z:.8f}\n")
