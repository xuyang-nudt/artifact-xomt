
#!/bin/bash
set -e

function dump_db(){
    local db=$1
    local dir=$(mktemp -d)
    pushd $dir > /dev/null
    sqlite3 $db .schema > schema.sql
    sqlite3 $db .dump > dump.sql
    grep -vx -f schema.sql dump.sql > data.sql
    rm schema.sql
    rm dump.sql
    echo $(pwd)/data.sql
    popd > /dev/null
}

function merge(){
    local db_a=$1
    local db_b=$2
    local out=$3
    local dir=$(mktemp -d)
    pushd $dir > /dev/null
    cp $db_a dbA.db
    cp $db_b dbB.db

    data_file=$(dump_db $(pwd)/dbA.db)
    sqlite3 dbB.db < $data_file
    mv dbB.db $out

    rm dbA.db
    rm $data_file

    popd > /dev/null
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --source-a)
            source_a="$2"
            shift 2
            ;;
        --source-b)
            source_b="$2"
            shift 2
            ;;
        --output)
            output="$2"
            shift 2
            ;;
        *)
            echo "Invalid option: $1"
            exit 1
            ;;
    esac
done

# Check if mandatory options are provided
if [[ -z "$source_a" || -z "$source_b" || -z "$output" ]]; then
    echo "Missing mandatory options. Please provide --source-a, --source-b, and --output."
    exit 1
fi

# Check if source files exist
if [[ ! -f "$source_a" ]]; then
    echo "Source file A does not exist: $source_a"
    exit 1
fi

if [[ ! -f "$source_b" ]]; then
    echo "Source file B does not exist: $source_b"
    exit 1
fi

source_a=$(realpath $source_a)
source_b=$(realpath $source_b)
output=$(realpath $output)

if [[ "$source_a" == *.zip ]]; then
    tmp=$(mktemp -d)
    unzip -j "$source_a" "output.db" -d "$tmp"
    source_a="$tmp/output.db"
fi

if [[ "$source_b" == *.zip ]]; then
    tmp=$(mktemp -d)
    unzip -j "$source_b" "output.db" -d "$tmp"
    source_b="$tmp/output.db"
fi

merge $source_a $source_b $output


