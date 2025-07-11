#!/bin/bash
# run with                      bash run.sh       | tee log.run
######################## TIC ###########################
set +e; start_time=$(date +%s%N)
######################## TIC ###########################

time_start=1 ; echo "time_start:" $time_start       # !=1 when restarting 
time_end=300 ; echo "time_end:" $time_end           # maximum number of iterations
nth_result=2                                        # print results only n-th iteration

rm -rf -v temporary
if [ "$time_start" -eq 1 ]; then
    bash clean.sh ; cp ../../MESH/beam_3D.med ./MESH.med
fi

set -e
cp ./ORG_3D/* .
echo "$PWD"/temporary   ;   sed -i "s|P rep_trav .*|P rep_trav $PWD/temporary|" *.export

cp Topology_Optimization.py Topology_Optimization_run.py
cp Postprocess.py Postprocess_run.py

aim_volume_fraction=$(grep -oP '^aim_volume_fraction\s*=\s*\K[0-9]+(\.[0-9]+)?' Topology_Optimization.py) ; echo "aim_volume_fraction:" $aim_volume_fraction
sed -i "s/^aim_volume_fraction = .*/aim_volume_fraction = $aim_volume_fraction/" Postprocess_run.py
for i in $(seq $time_start $time_end)
do
    start_time_it=$(date +%s%N)
    echo "Iteration:" $i
    j=$(echo "$i-1" | bc -l )
    cp Stage_1_Iteration.comm Stage_1_Iteration_${i}.comm
    cp Stage_1_Iteration.export Stage_1_Iteration_${i}.export
    sed -i "s/-time-/${i}/g" Stage_1_Iteration_${i}.export
    sed -i "s/^time_previous = .*/time_previous = ${j}/" Stage_1_Iteration_${i}.comm
    sed -i "s/^   aim_volume_fraction = .*/   aim_volume_fraction = $aim_volume_fraction/" Stage_1_Iteration_${i}.comm

if [ "$i" -eq 1 ]; then
    singularity run ~/salome_meca-lgpl-2022.1.0-1-20221225-scibian-9.sif shell << END
    as_run Stage_0_PreProcess.export
END
    singularity run ~/salome_meca-lgpl-2022.1.0-1-20221225-scibian-9.sif shell << END
    as_run Stage_1_Iteration_${i}.export
END
else
sed -i "s/^time_previous = .*/time_previous = $j/" Topology_Optimization_run.py
python3 Topology_Optimization_run.py

if (( i % nth_result != 0 )) && [ ! -e ./RESULTS/stop.txt ]; then
    sed -i 's/^F libr \.\/RESULTS\/R_1_Iteration/# &/' Stage_1_Iteration_${i}.export
fi

    singularity run ~/salome_meca-lgpl-2022.1.0-1-20221225-scibian-9.sif shell << END
    as_run Stage_1_Iteration_${i}.export
END

set +e
rm -rf -v base-Stage_TO*
if (( j % nth_result != 0 )); then
    rm ./RESULTS/VMIS_${j}.csv
    rm ./RESULTS/INVA_2_${j}.csv
    rm ./RESULTS/density_${j}.csv
else
    # python3 Postprocess_run.py
    echo ""
fi
set -e

fi

if [ -e ./RESULTS/stop.txt ]; then
    echo "stop.txt found. Exiting loop."
    echo ""
    break
fi

end_time_it=$(date +%s%N) ; elapsed_ns_it=$((end_time_it - start_time_it)) ; elapsed_ms_it=$((elapsed_ns_it / 1000000)) ; total_seconds_it=$((elapsed_ms_it / 1000))
hours_it=$((total_seconds_it / 3600)) ; minutes_it=$(( (total_seconds_it % 3600) / 60 )) ; seconds_it=$((total_seconds_it % 60)) ; milliseconds_it=$((elapsed_ms_it % 1000))  
printf "ITERATION - $i : ELAPSED TIME: %02d hr %02d min %02d.%03d s\n" $hours_it $minutes_it $seconds_it $milliseconds_it ; echo ""
done
set +e
python3 Postprocess_run.py

rm ./RESULTS/combined.mess *.comm *.export
cat ./RESULTS/*.mess >> ./RESULTS/combined.mess
bash backup.sh
du -sh RESULTS

######################## TOC ###########################
end_time=$(date +%s%N) ; elapsed_ns=$((end_time - start_time)) ; elapsed_ms=$((elapsed_ns / 1000000)) ; total_seconds=$((elapsed_ms / 1000))
hours=$((total_seconds / 3600)) ; minutes=$(( (total_seconds % 3600) / 60 )) ; seconds=$((total_seconds % 60)) ; milliseconds=$((elapsed_ms % 1000))  
basename $(pwd) ; printf "ELAPSED TIME: %02d hr %02d min %02d.%03d s\n" $hours $minutes $seconds $milliseconds | tee ./RESULTS/log.elapsed_time
######################## TOC ###########################


