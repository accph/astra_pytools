# astra_pytools
`Astra_pytools` is a set of tools for automation of using [**ASTRA**](https://www.desy.de/~mpyflo/) (**A** **S**pace Charge **Tr**acking **A**lgorithm) from DESY.

### Description
`Astra_pytools` includes the following modules.
1. `astratools` creates new input file for `ASTRA` with changed values of parameters from a pattern input file and run `ASTRA` simulation;
2. `astraproc` process output files of the simulation: return a beam in more suitable coordinates and/or the beam parameters (rms sizes, normalized emittances, Twiss parameters and dispersion function);
3. `cst2astra_3D` converts `CST studio suite` 3D field export files in `ASTRA` 3D  field  maps CAVITY format (see [**ASTRA**](https://www.desy.de/~mpyflo/) documetation);
4. `astra_M` calculate a transport matrix 6x6 of the beamline configured with `ASTRA` input file by tracking special defined beams in ASTRA. The coordinate vector is:
<p align="center">
  <img src="https://raw.githubusercontent.com/accph/astra_pytools/main/images/vect.gif" alt=""/>
</p>

### Requirements
- Python3
- numpy
- matplotlib

`ASTRA` executive file should be in `$PATH` or in working directory.

It was tested for Windows.

### Simple example of usage
Modules should be run in working directory (with `ASTRA` input/output files). 


### Example of usage
Simple example of running ASTRA calculations with quadrupoles currents changed.
```python
from astratools import make_file, run_ASTRA, remove_files
from astraproc import _process2, getEndParam

'''
    prepare input file with new parameters
'''
patt_name = 'drift' # name of pattern file
new_name = f'{patt_name}_0' # name of new file

remove_files(new_name) # remove files with new name if existing

params = { 'Q_grad(1)' : 1.5,
           'Q_grad(2)' : 1.6 } # parameters to change


'''
    make file and run ASTRA
'''
make_file(patt_name, new_name, params) # make new input file
run_ASTRA(new_name) # run ASTRA calculations


'''
    postprocessing
'''
data_name = f'{new_name}.0538.001' # output file name

beam, data = _process2(data_name) # postprocessing
print(getEndParam(beam)) # print beam parameters
```
