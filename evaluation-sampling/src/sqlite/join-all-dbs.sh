#!/bin/bash

set -x
set -e

function join_dbs() {
  local dbs_folder=$1
  local output_db=$2

  local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local JOIN_DB_SH="$script_dir/join-dbs.sh"
  
  # Enable nullglob option to handle no matches
  shopt -s nullglob

  # Get the list of databases in the folder using find and mapfile
  mapfile -t db_files < <(find "$dbs_folder" -type f -name '*.zip')

  # Disable nullglob option after getting the list of files
  shopt -u nullglob

  echo "db_files: ${db_files[@]}"

  # Check if there are no databases in the folder
  if [ ${#db_files[@]} -eq 0 ]; then
      echo "No databases found in the folder."
      return 1
  fi

  # Check if there is only one database in the folder
  if [ ${#db_files[@]} -eq 1 ]; then
      echo "Only one database found. Copying it to the output."
      cp "${db_files[0]}" "$output_db"
      return 0
  fi

  # Initialize the output database with the first database
  prev=$(mktemp --suffix=.zip)
  cp "${db_files[0]}" "$prev"

  # Iterate through the rest of the databases and join them
  for ((i = 1; i < ${#db_files[@]}; i++)); do
      db_b="${db_files[$i]}"
      # Run the join utility
      $JOIN_DB_SH --source-a "$prev" --source-b "$db_b" --output "$output_db"
      prev="$output_db"
  done

  echo "All databases have been joined into $output_db"
}

# Function to display usage information
usage() {
  echo "Usage: $0 --input-dir <input_directory> --output-db <output_database>"
  exit 1
}

# Check if at least 4 arguments are provided
if [ $# -ne 4 ]; then
  usage
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --input-dir)
      INPUT_DIR="$2"
      shift 2
      ;;
    --output-db)
      OUTPUT_DB="$2"
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
  echo "Error: Input directory '$INPUT_DIR' does not exist."
  exit 1
fi

# Check if output database file exists
if [ -e "$OUTPUT_DB" ]; then
  echo "Error: Output database '$OUTPUT_DB' already exists."
  exit 1
fi

join_dbs "$INPUT_DIR" "$OUTPUT_DB"