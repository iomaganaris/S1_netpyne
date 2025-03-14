
"""
netParams.py

High-level specifications for S1 network model using NetPyNE

Contributors: salvadordura@gmail.com, fernandodasilvaborges@gmail.com
"""

from netpyne import specs
import pickle, json
import os

netParams = specs.NetParams()   # object of class NetParams to store the network parameters


try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    from cfg import cfg

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# General network parameters
#------------------------------------------------------------------------------
netParams.scale = cfg.scale # Scale factor for number of cells
netParams.sizeX = cfg.sizeX # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.sizeY # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.sizeZ # z-dimension (horizontal depth) size in um
netParams.shape = 'cylinder' # cylindrical (column-like) volume
   
# Layer	height (um)	height (norma)	from	to
# L1	165		    0.079		    0.000	0.079
# L2	149		    0.072		    0.079	0.151
# L3	353		    0.170		    0.151	0.320
# L4	190		    0.091		    0.320	0.412
# L5	525		    0.252		    0.412	0.664
# L6	700		    0.336		    0.664	1.000
# L23	502		    0.241		    0.079	0.320
# All	2082	    1.000	

cellModels = ['HH_full']
Epops = ['L23_PC', 'L4_PC', 'L4_SS', 'L4_SP', 
             'L5_TTPC1', 'L5_TTPC2', 'L5_STPC', 'L5_UTPC',
             'L6_TPC_L1', 'L6_TPC_L4', 'L6_BPC', 'L6_IPC', 'L6_UTPC']
Ipops = []
for popName in cfg.popParamLabels:
    if popName not in Epops:
        Ipops.append(popName)

layer = {'1':[0.0, 0.079], '2': [0.079,0.151], '3': [0.151,0.320], '23': [0.079,0.320], '4':[0.320,0.412], '5': [0.412,0.664], '6': [0.664,1.0], 
'longS1': [2.2,2.3], 'longS2': [2.3,2.4]}  # normalized layer boundaries

# netParams.correctBorder = {'threshold': [cfg.correctBorderThreshold, cfg.correctBorderThreshold, cfg.correctBorderThreshold], 
#                         'yborders': [layer['1'][0], layer['2'][0], layer['6'][0], layer['6'][1]]}  # correct conn border effect

#------------------------------------------------------------------------------
# General connectivity parameters
#------------------------------------------------------------------------------
netParams.defaultThreshold = -10.0 # spike threshold, 10 mV is NetCon default, lower it for all cells
# netParams.defaultDelay = 2.0 # default conn delay (ms) (M1)
# netParams.propVelocity = 500.0 # propagation velocity (um/ms) (M1)
netParams.defaultDelay = 2.0 # default conn delay (ms)
netParams.propVelocity = 300.0 #  300 μm/ms (Stuart et al., 1997)

#------------------------------------------------------------------------------
# Cell parameters  # L1 70  L23 215  L4 230 L5 260  L6 260  = 1035
#------------------------------------------------------------------------------
folder = os.listdir('%s/cell_data/' % (cfg.rootFolder))
folder = sorted([d for d in folder if os.path.isdir('%s/cell_data/%s' % (cfg.rootFolder, d))])
folder = folder[0:5*int(cfg.celltypeNumber)] ## partial load to debug

## Load cell rules using BBP template
if cfg.importCellMod == 'BBPtemplate':

    def loadTemplateName(cellnumber):     
        outFolder = cfg.rootFolder+'/cell_data/'+folder[cellnumber]
        try:
            f = open(outFolder+'/template.hoc', 'r')
            for line in f.readlines():
                if 'begintemplate' in line:
                    return str(line)[14:-1]     
        except:
            print('Cannot read cell template from %s' % (outFolder))
            return False

    cellName = {}
    cellType = {}
    cellnumber = 0
    loadCellParams = folder
    for ruleLabel in loadCellParams:
        cellName[cellnumber] = ruleLabel
        cellTemplateName = loadTemplateName(cellnumber)
        # print(cellName[cellnumber], cellTemplateName)
        if cellTemplateName:
            cellRule = netParams.importCellParams(label=cellName[cellnumber], somaAtOrigin=False,
                conds={'cellType': cellName[cellnumber], 'cellModel': 'HH_full'},
                fileName='cellwrapper.py',
                cellName='loadCell',
                cellInstance = True,
                cellArgs={'cellName': cellName[cellnumber], 'cellTemplateName': cellTemplateName})
            netParams.renameCellParamsSec(label=cellName[cellnumber], oldSec='soma_0', newSec='soma')
            os.chdir(cfg.rootFolder)
        cellnumber = cellnumber + 1

## Load cell rules previously saved using netpyne format before popParams
if cfg.importCellMod == 'pkl_before':
    loadCellParams = folder
    cellName = {}
    cellnumber = 0
    for ruleLabel in loadCellParams:
        cellName[cellnumber] = ruleLabel
        netParams.loadCellParamsRule(label = ruleLabel, fileName = 'cell_data/' + ruleLabel + '/' + ruleLabel + '_cellParams.pkl')    
        netParams.renameCellParamsSec(label=cellName[cellnumber], oldSec='soma_0', newSec='soma')
        cellnumber = cellnumber + 1

#------------------------------------------------------------------------------
# Population parameters
#------------------------------------------------------------------------------
for popName in cfg.popParamLabels:
	layernumber = popName[1:2]
	if layernumber == '2':
		netParams.popParams[popName] = {'cellType': popName, 'cellModel': 'HH_full', 'ynormRange': layer['23'], 'numCells': int(cfg.scaleDensity*cfg.popNumber[popName]+0.5), 'diversity': cfg.celldiversity}
	else:
		netParams.popParams[popName] = {'cellType': popName, 'cellModel': 'HH_full', 'ynormRange': layer[layernumber], 'numCells': int(cfg.scaleDensity*cfg.popNumber[popName]+0.5), 'diversity': cfg.celldiversity}

## Cell property rules
# cfg.reducedtest = True
cellnumber = 0    
if cfg.celldiversity:
    for cellName in cfg.cellParamLabels:
        
        if cfg.cellNumber[cellName] < 5:
            morphoNumbers = cfg.cellNumber[cellName]
        else:
            morphoNumbers = 5
        
        popName = cfg.popLabel[cellName]
        cellFraction = 1.0*cfg.cellNumber[cellName]/(morphoNumbers*cfg.popNumber[popName])
        
        if cfg.verbose:
            print(popName,cellName,cfg.cellNumber[cellName],cfg.popNumber[popName],morphoNumbers*cellFraction)
            print('diversityFraction =',morphoNumbers*cellFraction)

        for morphoNumber in range(morphoNumbers):
            cellMe = cellName + '_' + str(morphoNumber+1)
            ## Load cell rules previously saved using netpyne format
            if cfg.importCellMod == 'pkl_after':
                netParams.loadCellParamsRule(label = cellMe, fileName = 'cell_data/' + cellMe + '/' + cellMe + '_cellParams.pkl')    
                netParams.renameCellParamsSec(label = cellMe, oldSec = 'soma_0', newSec = 'soma')

            cellRule = {'conds': {'cellType': popName}, 'diversityFraction': cellFraction, 'secs': {}}  # cell rule dict
            cellRule['secs'] = netParams.cellParams[cellMe]['secs']     
            cellRule['conds'] = netParams.cellParams[cellMe]['conds']    
            cellRule['conds']['cellType'] = popName
            cellRule['globals'] = netParams.cellParams[cellMe]['globals']       
            cellRule['secLists'] = netParams.cellParams[cellMe]['secLists']                 
            cellRule['secLists']['all'][0] = 'soma' # replace 'soma_0'
            cellRule['secLists']['somatic'][0]  = 'soma' # replace 'soma_0'

            # nonSpiny = ['axon_0', 'axon_1']
            # netParams.addCellParamsSecList(label=cellMe, secListName='spiny')  # section
            # cellRule['secLists']['spiny'] = [sec for sec in cellRule['secLists']['all'] if sec not in nonSpiny]

            # if cfg.reducedtest:
            #     cellRule['secs'] = {}
            #     cellRule['secs']['soma'] = netParams.cellParams[cellMe]['secs']['soma']   
                # cellRule['secs']['dend_0'] = netParams.cellParams[cellMe]['secs']['dend_0']   
                # cellRule['secs']['dend_1'] = netParams.cellParams[cellMe]['secs']['dend_1']    
                # cellRule['secs']['axon_0']  = netParams.cellParams[cellMe]['secs']['axon_0']   
                # cellRule['secs']['axon_1'] = netParams.cellParams[cellMe]['secs']['axon_1']      
                # if 'apic_1' in cellRule['secLists']['apical']:
                #     cellRule['secs']['apic_0']  = netParams.cellParams[cellMe]['secs']['apic_0']
                #     cellRule['secs']['apic_1']  = netParams.cellParams[cellMe]['secs']['apic_1']

            netParams.cellParams[cellMe] = cellRule   # add dict to list of cell params   

            cellnumber=cellnumber+1  	
            

#------------------------------------------------------------------------------
# Synaptic mechanism parameters
#------------------------------------------------------------------------------
# TABLE -  S6
# ConnectionType gsynM gsynStd t_riseM t_riseStd t_decayM t_decayStd 
# L23_PC:L23_PC 0.68 0.46 0.2 0.1 1.7 0.14 
# L4_exc:L4_exc 0.68 0.45 0.2 0.1 1.7 0.14 
# L4_SS:L23_PC 0.19 0.2 0.1 1.7 0.14 
# L5_TTPC:L5_TTPC 1.5 0.12 0.2 0.1 1.7 0.14 1.05 
# L5_STPC:L5_STPC 0.8 0.53 0.2 0.1 1.7 0.14 
# exc:exc 0.72 0.5 0.2 0.1 1.7 0.14
# L5_TTPC:L5_MC 0.11 0.08 0.2 0.1 1.7 0.14
# L5_PC:L5_ChC 0.72 0.5 0.2 0.1 1.7 0.14
# L5_BC:L5_ChC 0.72 0.5 0.2 0.1 1.7 0.14
# exc:inh 0.43 0.28 0.2 0.1 1.7 0.14
# L5_MC:L5_TTPC 0.75 0.32 0.2 0.1 8.3 2.2
# L23_NBC:L23_ChC 0.91 0.61 0.2 0.1 8.3 2.2
# L23_LBC:L23_ChC 0.91 0.61 0.2 0.1 8.3 2.2
# L23_NBC:L23_PC 0.91 0.61 0.2 0.1 8.3 2.2
# L23_LBC:L23_PC 0.91 0.61 0.2 0.1 8.3 2.2
# inh:exc 0.83 0.2 0.2 0.1 8.3 2.2   
# inh:inh 0.83 0.55 0.2 0.1 8.3 2.2

### mods from M1 detailed
netParams.synMechParams['AMPA'] = {'mod':'MyExp2SynBB', 'tau1': 0.2, 'tau2': 1.74, 'e': 0}
netParams.synMechParams['NMDA'] = {'mod': 'MyExp2SynNMDABB', 'tau1NMDA': 0.29, 'tau2NMDA': 43, 'e': 0}
netParams.synMechParams['GABAA'] = {'mod':'MyExp2SynBB', 'tau1': 0.2, 'tau2': 8.3, 'e': -80}
netParams.synMechParams['GABAB'] = {'mod':'MyExp2SynBB', 'tau1': 3.5, 'tau2': 260.9, 'e': -93} 

ESynMech = ['AMPA', 'NMDA']
ISynMech = ['GABAA', 'GABAB']

#------------------------------------------------------------------------------
# Local connectivity parameters
#------------------------------------------------------------------------------

## load data from conn pre-processing file
with open('conn/conn.pkl', 'rb') as fileObj: connData = pickle.load(fileObj)
pmat = connData['pmat']
lmat = connData['lmat']
wmat = connData['wmat']
connDataSource = connData['connDataSource']
epsp = connData['epsp']
gsyn = connData['gsyn']
a0mat = connData['a0mat']
 

#------------------------------------------------------------------------------
## E -> E/I
if cfg.addConn:
    for pre in Epops:
        for post in Epops+Ipops:
            # prob = '%f * exp(-dist_2D/%f)' % (a0mat[pre][post], lmat[pre][post])
            prob = '%f * 0.01 * exp(-dist_2D/%f)' % (a0mat[pre][post], lmat[pre][post])
            
            netParams.connParams['EE_'+pre+'_'+post] = { 
                'preConds': {'pop': pre}, 
                'postConds': {'pop': post},
                'synMech': ESynMech,
                'probability': prob,
                'weight': gsyn[pre][post] * cfg.EEGain, 
                'synMechWeightFactor': cfg.synWeightFractionEE,
                'delay': 'defaultDelay+dist_3D/propVelocity',
                'synsPerConn': 1,
                'sec': 'all'}     
#------------------------------------------------------------------------------           
## I -> E/I
if cfg.addConn:
    for pre in Ipops:
        for post in Epops+Ipops:
            # prob = '%f * exp(-dist_2D/%f)' % (a0mat[pre][post], lmat[pre][post])
            prob = '%f * 0.01 * exp(-dist_2D/%f)' % (a0mat[pre][post], lmat[pre][post])
            
            netParams.connParams['II_'+pre+'_'+post] = { 
                'preConds': {'pop': pre}, 
                'postConds': {'pop': post},
                'synMech': ISynMech,
                'probability': prob,
                'weight': gsyn[pre][post] * cfg.IIGain, 
                'synMechWeightFactor': cfg.synWeightFractionII,
                'delay': 'defaultDelay+dist_3D/propVelocity',
                'synsPerConn': 1,
                'sec': 'all'}   
    
#------------------------------------------------------------------------------
# Current inputs (IClamp)
#------------------------------------------------------------------------------
if cfg.addIClamp:
     for j in range(cfg.IClampnumber):
        key ='IClamp'
        params = getattr(cfg, key, None)
        key ='IClamp'+str(j+1)
        params = params[j]
        [pop,sec,loc,start,dur,amp] = [params[s] for s in ['pop','sec','loc','start','dur','amp']]

        # add stim source
        netParams.stimSourceParams[key] = {'type': 'IClamp', 'delay': start, 'dur': dur, 'amp': amp}
        
        # connect stim source to target
        netParams.stimTargetParams[key+'_'+pop] =  {
            'source': key, 
            'conds': {'pop': pop},
            'sec': sec, 
            'loc': loc}
#------------------------------------------------------------------------------
# Description
#------------------------------------------------------------------------------
netParams.description = """ 
- Code based: M1 net, 6 layers, 7 cell types - v103
- v0 - insert cell diversity
- v1 - insert connection rules
"""