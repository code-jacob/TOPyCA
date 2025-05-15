# TOPyCA - Topology Optimization with Python and code_aster

The idea is to use code_aster to solve simple static analysis and print VMIS of node group called "REGION" to .txt. 
Next, use a python code to calculate new density using this file and this density distribution then map as Young's modulus 
onto a mesh in a new analysis and solve.
And so on..

The whole SIMP method is written in python file so it is basically code_aster + python or more precisely bash + code_aster + python coupling,
thus every stage is done separately and the loops are not done inside one code_aster run. This way leads to:

- postprocessing can be done when optimization is running
- code is more comprehensible
- possibility to change parameters manually when running, for example target volume fraction, penalization factor etc.
- possibility to restart optimization from specified iteration
- easily add new manufacturing constrains
- it can be modified and used for shells or 2D/axisymmetry as well (DKT tested so far)
- for small cases the most time consuming part is start up of code_aster, the solution of linear static and calculation of densities takes only a second

**NOTES**:

• Element volume is considered constant so far, however to create uniform mesh is quite easy for optimization domain, since usually it has simple shape. Moreover, uniform high mesh density is needed anyway...

• Stamping and casting manufacturing constraints are implemented only for cartesian direction to increase performance since in 
99% of cases an arbitrary direction is not needed (but with a little effort it could be implemented as well). However, user has to switch manually COOR_X, COOR_Y, COOR_Z in the function.

• For symmetry manufacturing constraint, an arbitrary direction is implemented.

• To use more than one symmetry constraint, user has to copy the function and rename it for example to symmetry_constraint_2, and apply the constraints sequentially. However, I have not tested it yet.

More on: https://forum.code-aster.org/public/d/20385-topological-optimization/13

<div align="center">
    <img src="./IMAGES/beam_TO.gif" width="800">
    <br><br>
    <img src="./IMAGES/clip/clip_TO_2.gif" width="800">
</div>

## Prerequisites

- code_aster (tested version is 15.4, 16.2)
- python3 with all necessary libraries, for example Anaconda distribution

After downloading, you have to change all lines containing
```bash
$ singularity run ~/salome_meca-lgpl-2022.1.0-1-20221225-scibian-9.sif shell << END
```
according to your container name in file **run.sh**.
If you use code_aster without salome_meca, then delete these lines (lines with END also).

## How to run

Just change directory to ./beam and enter

```bash
$ bash run.sh
```
or

```bash
$ bash run.sh       | tee log.run
```

## Post-Process

- In Paraview go to Python Shell and click on Run Script
- open state_1.pvsm

or do it manually

- In Paraview click on Open File, RESULTS, all_density.csv
- select Temporal CSV Reader
- in Field Delimeter Characters enter ,
- in Time Column Name enter INST
- apply filter TableToPoints
- change X Column to COOR_X, Y Column to COOR_Y, Z Column to COOR_Z

- open file MESH_GROUPS.med
- apply filter ExtractGroup, select UNAFFECTED
- apply filter ExtractGroup, select REGION
- apply filter PointDatasetInterpolator - Input > TableToPoints, Source > ExtractGroup (REGION)
- ( or apply filter ResampleWithDataset - Source Data Arrays > TableToPoints, Destination Mesh > ExtractGroup (REGION), then tick Snap To Cell With Closest Point, untick Compute Tolerance ) # much slower

How to extract 3D shape:
- apply filter Clip
- Clip Type -> Scalar -> density
- value -> for example 0.5

Eventually you can smooth the final shape:
- apply filter Extract Surface
- apply filter Smooth -> Number of Iterations -> 500


**NOTE**: For large studies instead of selecting all_density.csv select density_{iteration}.csv. 
For updating: right click - Change File - select different density_{iteration}.csv.



## How to cite 
If you've used TOPyCA in your research or work, or find it useful in any way, please consider to cite:
```
@misc{code-jacob,
  title = {TOPyCA - Topology Optimization with Python and code_aster},
  author = {Jakub Trušina}, 
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/code-jacob/TOPyCA}},
}
```