# trace generated using paraview version 5.11.0
#import paraview
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 11

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'Temporal CSV Reader'
all_densitycsv = TemporalCSVReader(registrationName='all_density.csv', FileName='C:\\Users\\trusinja\\Desktop\\ASTER_WORK\\AG_WORK\\TOPyCA\\STUDY\\beam\\RESULTS\\all_density.csv')
all_densitycsv.TimeColumnName = ''

# Properties modified on all_densitycsv
all_densitycsv.FieldDelimiterCharacters = ','
all_densitycsv.TimeColumnName = 'INST'

UpdatePipeline(time=0.0, proxy=all_densitycsv)

# get animation scene
animationScene1 = GetAnimationScene()

# get the time-keeper
timeKeeper1 = GetTimeKeeper()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# create a new 'Table To Points'
tableToPoints1 = TableToPoints(registrationName='TableToPoints1', Input=all_densitycsv)
tableToPoints1.XColumn = 'COOR_X'
tableToPoints1.YColumn = 'COOR_X'
tableToPoints1.ZColumn = 'COOR_X'

# Properties modified on tableToPoints1
tableToPoints1.YColumn = 'COOR_Y'
tableToPoints1.ZColumn = 'COOR_Z'

UpdatePipeline(time=1.0, proxy=tableToPoints1)

# create a new 'MED Reader'
mESH_GROUPSmed = MEDReader(registrationName='MESH_GROUPS.med', FileNames=['C:\\Users\\trusinja\\Desktop\\ASTER_WORK\\AG_WORK\\TOPyCA\\STUDY\\beam\\MESH_GROUPS.med'])
mESH_GROUPSmed.FieldsStatus = ['TS0/00000001/ComSup0/00000001@@][@@P0']
mESH_GROUPSmed.VectorsProperty = 1
mESH_GROUPSmed.TimesFlagsStatus = ['0000']

UpdatePipeline(time=0.0, proxy=mESH_GROUPSmed)

# create a new 'Extract Group'
extractGroup1 = ExtractGroup(registrationName='ExtractGroup1', Input=mESH_GROUPSmed)
extractGroup1.AllGroups = []

# Properties modified on extractGroup1
extractGroup1.AllGroups = ['GRP_SHELL']

UpdatePipeline(time=0.0, proxy=extractGroup1)

# create a new 'Resample With Dataset'
resampleWithDataset1 = ResampleWithDataset(registrationName='ResampleWithDataset1', SourceDataArrays=tableToPoints1,
    DestinationMesh=extractGroup1)
resampleWithDataset1.PassCellArrays = 1
resampleWithDataset1.PassPointArrays = 1
resampleWithDataset1.ComputeTolerance = 0
resampleWithDataset1.SnapToCellWithClosestPoint = 1
resampleWithDataset1.CellLocator = 'Static Cell Locator'

UpdatePipeline(time=0.0, proxy=resampleWithDataset1)

# set active source
SetActiveSource(resampleWithDataset1)

UpdatePipeline(time=0.0, proxy=resampleWithDataset1)

animationScene1.GoToLast()

# set active source
SetActiveSource(resampleWithDataset1)

# create a new 'Annotate Time Filter'
annotateTimeFilter1 = AnnotateTimeFilter(registrationName='AnnotateTimeFilter1', Input=resampleWithDataset1)
annotateTimeFilter1.Format = 'Time: {time:.0f}'

UpdatePipeline(time=5.0, proxy=annotateTimeFilter1)

# set active source
SetActiveSource(resampleWithDataset1)

# create a new 'Point Data to Cell Data'
pointDatatoCellData1 = PointDatatoCellData(registrationName='PointDatatoCellData1', Input=resampleWithDataset1)
pointDatatoCellData1.PointDataArraytoprocess = ['ENERGY', 'FamilyIdNode', 'INVA_2', 'VMIS', 'density', 'vtkValidPointMask', '00000001', 'FamilyIdCell', 'NumIdCell']

# Properties modified on pointDatatoCellData1
pointDatatoCellData1.PassPointData = 1

UpdatePipeline(time=5.0, proxy=pointDatatoCellData1)