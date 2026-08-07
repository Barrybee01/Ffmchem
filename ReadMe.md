# Ffmchem

I will be slowly developing a command-line tool so that all of the converter scripts can be used with only one tool. These will be the converter options:

- `.lmp` ↔ `.xyz`
- `.lmp` to a modified `.xyz` format
- `.lammpstrj` to a `.xyz` trajectory
- `.lammpstrj` to a modified `.xyz` trajectory
- `.cif` ↔ `.lmp` 
- `.xyz` ↔ `.cif` 
- `.vasp` ↔ `.xyz`

## Data Prerequisites:
- `.xyz` files need to have the cell parameters in the comment line.

## Dependencies:
- Python >= 3.9
- Numpy

## Installation Instructions
Do the following for any Python environment::

```
git clone https://github.com/Barrybee01/Ffmchem.git
cd Ffmchem
python -m pip install -e .
```

Because this tool was installed this way, updating the tool does not require it to be reinstalled. Instead, do the following:

```
cd Ffmchem
git pull
python -m pip install -e .
```

## How To Use
Some structure files are available in the examples folder to use for testing. The available arguments in the tool are:

```
--help          Give the list of commands and what they do
--input         Input file for single conversion, or input directory when using batch analysis
--output        Output file for single conversion or output directory when using batch analysis
--from          The input file format
--to            The output file format
--map           Some conversions require an atom type map that relates a numerical index to an atom type. More information provided below
--mass-map      Similar to the atomic map, but includes atomic mass. This is needed for conversions to lmp format
--batch         Allows a user to perform file conversions from a folder with many structure files
--atom-centric  Takes the input file and makes a series of output files for each atom type
--coordinates   The coordinate type used in a LAMMPS simulation (scaled, unscaled, wrapped). This can be specified or automatically detected
--lattice-type  The lattice type needs to be entered for conversion to cif file format
--space-group   The space group of the lattice needs to be entered for conversion to cif file format
--split         Splits the trajectory into its individual time steps in either xyz format or lammpstrj format
```
There are a few cases where an atomic map is required:  `.lmp` to `.cif`, `.lmp` to `.xyz`, `.cif` to `.lmp` and `.xyz` to `.lmp`. For example,

```
ffmchem --input structure.lmp --output structure.xyz --from lmp --to xyz --map 1:O 2:H
```

A mass map is required when converting file types into `.lmp` format. For example,

```
ffmchem --input structure.xyz --output structure.lmp --from xyz --to lmp --map 1:O 2:H --mass-map 1:16 2:1
```

For batch analysis, you enter the input and output directories. For example, a case where you would perform batch analysis and make files for individual atom types will look like,

```
ffmchem --input /lmp/input/dir --output /xyz/output/dir --from lmp --to xyz --map 1:O 2:H --batch --atom-centric
```

***At present, batch analysis only works when making `.xyz ` files***
