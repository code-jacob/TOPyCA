#!/bin/bash

# Get the parent directory name (two levels up)
parent_dir_name=$(basename "$(dirname "$(dirname "$(pwd)")")")

# Get the current directory name
current_dir_name=$(basename "$(pwd)")

# Get the current date and time
current_date_time=$(date +"%H-%M-%S-%d-%m-%Y")

# Create the folder with the current date and time
folder_name="$parent_dir_name"-"$current_dir_name"-"$current_date_time"

copy_to=/mnt/c/users/trusinja/AppData/Local/Temp
mkdir $copy_to/$folder_name && cp -a ORG/. $_ && cp ./RESULTS/*.mess $_ 

echo "Created backup ORG folder: $folder_name in $copy_to"
