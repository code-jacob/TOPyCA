# TOPyCA - Topology Optimization with Python and code_aster

<div align="center">
    <img src="./imgsrc/beam_TO.gif" width="800">
    <br><br>
    <img src="./imgsrc/clip_TO_2.gif" width="800">
</div>

## Prerequisites

- code_aster (tested version is 15.4)
- python3 with all necessary libraries, for example Anaconda distribution

After downloading, you have to change all lines containing
```bash
$ singularity run ~/salome_meca-lgpl-2021.0.0-0-20210601-scibian-9.sif shell << END
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
- open trace_1.py (you have to change paths of all_density.csv and MESH_GROUPS.med according to your system)

or do it manually

- In Paraview click on Open File, RESULTS, all_density.csv
- select Temporal CSV Reader
- in Field Delimeter Characters enter ,
- in Time Column Name enter INST
- apply filter TableToPoints
- change X Column to COOR_X, Y Column to COOR_Y, Z Column to COOR_Z

- open file MESH_GROUPS.med
- apply filter ExtractGroup, select ALL_VOLUMES
- apply filter ExtractGroup, select REGION
- apply filter ResampleWithDataset - Source Data Arrays > TableToPoints, Destination Mesh > ExtractGroup (REGION)
- tick Snap To Cell With Closest Point, untick Compute Tolerance

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
{ title = {TOPyCA - Topology Optimization with Python and code_aster},
  author = {Jakub Trušina}, 
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/code-jacob/to}},
}
```