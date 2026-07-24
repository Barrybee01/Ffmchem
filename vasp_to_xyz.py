import numpy as np
import os

def parse_poscar(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    if len(lines) < 8:
        raise ValueError(f"POSCAR file {filename} is too short or malformed.")
    
    # Skip comment line (line 0)
    # Line 1: scaling factor
    try:
        scaling = float(lines[1].strip())
    except ValueError:
        scaling = 1.0
    
    # Lines 2-4: lattice vectors
    lattice_vectors = []
    for i in range(2, 5):
        parts = lines[i].strip().split()
        if len(parts) < 3:
            raise ValueError(f"Invalid lattice vector on line {i+1}: {lines[i]}")
        try:
            vec = [float(x) * scaling for x in parts[:3]]
            lattice_vectors.append(vec)
        except ValueError:
            raise ValueError(f"Invalid lattice vector on line {i+1}: {lines[i]}")
    
    lattice_vectors = np.array(lattice_vectors)
    
    # Line 5: atom types
    atom_types = lines[5].strip().split()
    
    # Line 6: atom counts
    try:
        atom_counts = [int(x) for x in lines[6].strip().split()]
    except ValueError:
        raise ValueError(f"Invalid atom counts on line 7: {lines[6]}")
    
    # Check if coordinate system is specified on line 7
    coord_line = lines[7].strip().lower()
    if 'cartesian' in coord_line or 'cart' in coord_line:
        coordinate_system = 'Cartesian'
        coord_start = 8
    elif 'direct' in coord_line or 'frac' in coord_line:
        coordinate_system = 'Direct'
        coord_start = 8
    else:
        # No coordinate system specified, assume Direct (VASP default)
        coordinate_system = 'Direct'
        coord_start = 7
    
    # Parse coordinates
    coordinates = []
    total_atoms = sum(atom_counts)
    coord_idx = 0
    
    for i, count in enumerate(atom_counts):
        for _ in range(count):
            if coord_idx + coord_start >= len(lines):
                break
            parts = lines[coord_start + coord_idx].strip().split()
            if len(parts) >= 3:
                try:
                    x, y, z = map(float, parts[:3])
                    coordinates.append([x, y, z])
                except ValueError:
                    break
            coord_idx += 1
    
    if len(coordinates) == 0:
        raise ValueError(f"No coordinates found in POSCAR file {filename}")
    
    return lattice_vectors, atom_types, atom_counts, np.array(coordinates), coordinate_system

def fractional_to_cartesian(fractional_coords, lattice_vectors):
    return np.dot(fractional_coords, lattice_vectors)

def write_xyz_file(filename, atom_data, lattice_vectors):
    a = np.linalg.norm(lattice_vectors[0])
    b = np.linalg.norm(lattice_vectors[1])
    c = np.linalg.norm(lattice_vectors[2])
    
    # Calculate triclinic parameters (xy, xz, yz)
    v1 = lattice_vectors[0]
    v2 = lattice_vectors[1]
    v3 = lattice_vectors[2]
    
    # Dot products for triclinic parameters
    xy = np.dot(v2, v1) / a if a > 0 else 0
    xz = np.dot(v3, v1) / a if a > 0 else 0
    yz = np.dot(v3, v2) / b if b > 0 else 0
    
    with open(filename, 'w') as f:
        # Write number of atoms
        f.write(f"{len(atom_data)}\n")
        # Write comment line with cell parameters
        f.write(f"{a:.12f} {b:.12f} {c:.12f} {xy:.12f} {xz:.12f} {yz:.12f}\n")
        # Write atom data
        for element, x, y, z in atom_data:
            f.write(f"{element} {x:.12f} {y:.12f} {z:.12f}\n")

def convert_vasp_to_xyz(input_file, output_file):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} does not exist")
    
    # Parse POSCAR file
    lattice_vectors, atom_types, atom_counts, coordinates, coordinate_system = parse_poscar(input_file)
    
    # Convert coordinates to Cartesian if in Direct format
    if coordinate_system == 'Direct':
        coordinates = fractional_to_cartesian(coordinates, lattice_vectors)
    
    # Build atom_data with atom types directly from POSCAR
    atom_data = []
    coord_idx = 0
    
    for i, atom_type in enumerate(atom_types):
        count = atom_counts[i]
        for _ in range(count):
            if coord_idx < len(coordinates):
                x, y, z = coordinates[coord_idx]
                atom_data.append((atom_type, x, y, z))
                coord_idx += 1
    
    # Write XYZ file
    write_xyz_file(output_file, atom_data, lattice_vectors)
    
    return atom_data
