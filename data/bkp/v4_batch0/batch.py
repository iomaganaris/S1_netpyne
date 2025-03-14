"""
batch.py 

Batch simulation for S1 model using NetPyNE

Contributors: salvadordura@gmail.com, fernandodasilvaborges@gmail.com
"""
from netpyne.batch import Batch
from netpyne import specs
import numpy as np

# ----------------------------------------------------------------------------------------------
# Custom
# ----------------------------------------------------------------------------------------------
def custom():
    params = specs.ODict()
    
    params[('seeds', 'conn')] =  [2033] 
    # params[('seeds', 'conn')] =  [2201, 2202, 2203, 2204] 
    # params[('importCellMod')] = ['BBPtemplate','pkl_before','pkl_after']

    b = Batch(params=params, netParamsFile='netParams.py', cfgFile='cfg.py')

    return b

# ----------------------------------------------------------------------------------------------
# Run configurations
# ----------------------------------------------------------------------------------------------
def setRunCfg(b, type='mpi_bulletin'):
    if type=='mpi_bulletin' or type=='mpi':
        b.runCfg = {'type': 'mpi_bulletin', 
            'script': 'init.py', 
            'skip': True}

    elif type=='mpi_direct':
        b.runCfg = {'type': 'mpi_direct',
            'cores': 200,
            'script': 'init.py',
            'mpiCommand': 'mpiexec', 
            'skip': True}

    elif type=='hpc_slurm_gcp':
        b.runCfg = {'type': 'hpc_slurm', 
            'allocation': 'default',
            'walltime': '24:00:00', 
            'nodes': 1,
            'coresPerNode': 96,
            'email': 'salvadordura@gmail.com',
            'folder': '/home/ext_salvadordura_gmail_com/m1/sim/', 
            'script': 'init.py', 
            'mpiCommand': 'mpirun',
            'skipCustom': '_raster.png'}

# ----------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------
if __name__ == '__main__': 
    b = custom() #

    b.batchLabel = 'v4_batch0'  
    b.saveFolder = '../data/'+b.batchLabel
    b.method = 'grid'
    setRunCfg(b, 'mpi_direct')     # setRunCfg(b, 'mpi_bulletin')
    b.run() # run batch
