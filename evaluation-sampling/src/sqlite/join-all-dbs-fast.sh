#!/bin/bash

set -e

function dump_db(){
    local db=$1
    local dir="$(mktemp -d)"
    pushd $dir > /dev/null
    sqlite3 $db .schema > schema.sql
    sqlite3 $db .dump > dump.sql
    grep -vx -f schema.sql dump.sql > data.sql
    rm schema.sql
    rm dump.sql
    echo "$(pwd)/data.sql"
    popd > /dev/null
}

function merge(){ # merges db_a into db_b in place
    local db_a=$1
    local db_b=$2
    local out=$3
    #local dir=$(mktemp -d)
    #pushd $dir > /dev/null

    data_file=$(dump_db "$db_a")
    sqlite3 "$db_b" < "$data_file"
    rm $data_file

    #popd > /dev/null
}

function join_dbs() {
  local dbs_folder=$1
  local output_db=$2

  local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local JOIN_DB_SH="$script_dir/join-dbs.sh"
  
  # Enable nullglob option to handle no matches
  shopt -s nullglob

  # Get the list of databases in the folder using find and mapfile
  mapfile -t zip_files < <(find "$dbs_folder" -type f -name '*.zip')

  # Disable nullglob option after getting the list of files
  shopt -u nullglob

  echo "zip_files: ${zip_files[@]}"

  # Check if there are no databases in the folder
  if [ ${#zip_files[@]} -eq 0 ]; then
      echo "No databases found in the folder."
      return 1
  fi

  # Check if there is only one database in the folder
  if [ ${#zip_files[@]} -eq 1 ]; then
      echo "Only one database found. Copying it to the output."
      local tmp_dir="$(mktemp -d)"
      unzip -j "${zip_files[0]}" "output.db" -d "$tmp_dir"
      mv "$tmp_dir/output.db" "$output_db"
      return 0
  fi

  # Initialize the output database with the first database
  local prev_zip="${zip_files[0]}"
  prev_zip="$(realpath "$prev_zip")"

  local prev_db="$(mktemp -d)"
  unzip -j "$prev_zip" "output.db" -d "$prev_db"
  prev_db="$prev_db/output.db"

  local current_dir="$(mktemp -d)"
  # Iterate through the rest of the databases and join them
  for ((i = 1; i < ${#zip_files[@]}; i++)); do
      echo "Processing ZIP file $i"
      current_zip="${zip_files[$i]}"
      local current_db="$current_dir"
      unzip -j "$current_zip" "output.db" -d "$current_db"
      current_db="$current_db/output.db"
      merge "$current_db" "$prev_db"
      rm "$current_db"
  done

  mv "$prev_db" "$output_db"

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
      output_zip="$2"
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
if [ -e "$output_zip" ]; then
  echo "Error: Output database '$output_zip' already exists."
  exit 1
fi

join_dbs "$INPUT_DIR" "$output_zip"