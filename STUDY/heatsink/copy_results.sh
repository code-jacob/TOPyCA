
result_folder=RESULTS_1


copy_to=/mnt/d/ASTER_RESULTS/

case_name=$(basename "$(dirname "$(dirname "$(pwd)")")")
load_case_name=$(basename "$(pwd)")
folder_name="$result_folder"_"$load_case_name"_"$case_name"

final_directory=$copy_to/$case_name/$load_case_name/$folder_name

# rm -rf $final_directory
mkdir -p $final_directory   && cp -a RESULTS/. $final_directory  &&  cp -r ORG $final_directory

echo "Results copied to: $final_directory"


