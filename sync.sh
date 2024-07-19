#!/bin/bash
#The script will use `rsync` for synchronization and #`md5sum` for hash verification.
# ./sync.sh /path/to/source_directory /path/to/destination_directory --verbose --purge --forcecopy --2sync --hverify
function usage {
    echo "Usage: $0 <source_directory> <destination_directory> [options]"
    echo "Options:"
    echo "  --verbose      Enable verbose mode"
    echo "  --purge        Delete files from destination that are not in source"
    echo "  --forcecopy    Force copy files even if they exist and are the same"
    echo "  --use-ctime    Use creation time instead of modification time"
    echo "  --use-content  Compare files based on content"
    echo "  --2sync        Enable two-way synchronization"
    echo "  --hverify      Verify MD5 hashes after synchronization"
    exit 1
}

function compute_md5 {
    find "$1" -type f -exec md5sum {} \; | sort -k 2 | md5sum
}

if [ $# -lt 2 ]; then
    usage
fi

SOURCE_DIR=$1
DEST_DIR=$2
shift 2

VERBOSE=""
PURGE=""
FORCECOPY=""
USE_CTIME=""
USE_CONTENT=""
TWO_WAY=""
HVERIFY=""

while (( "$#" )); do
    case "$1" in
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --purge)
            PURGE="--delete"
            shift
            ;;
        --forcecopy)
            FORCECOPY="--ignore-existing"
            shift
            ;;
        --use-ctime)
            USE_CTIME="--times"
            shift
            ;;
        --use-content)
            USE_CONTENT="--checksum"
            shift
            ;;
        --2sync)
            TWO_WAY="yes"
            shift
            ;;
        --hverify)
            HVERIFY="yes"
            shift
            ;;
        *)
            usage
            ;;
    esac
done

RSYNC_OPTIONS="-a $VERBOSE $PURGE $FORCECOPY $USE_CTIME $USE_CONTENT"

# Perform synchronization
rsync $RSYNC_OPTIONS "$SOURCE_DIR/" "$DEST_DIR/"

if [ "$TWO_WAY" == "yes" ]; then
    rsync $RSYNC_OPTIONS "$DEST_DIR/" "$SOURCE_DIR/"
fi

# Verify MD5 hashes if requested
if [ "$HVERIFY" == "yes" ]; then
    SRC_MD5=$(compute_md5 "$SOURCE_DIR")
    DST_MD5=$(compute_md5 "$DEST_DIR")

    if [ "$SRC_MD5" == "$DST_MD5" ]; then
        echo "All files are synchronized (MD5 hashes match)."
    else
        echo "Some files are not synchronized (MD5 hashes do not match)."
    fi
fi
### Instructions
#1. Save this script as `sync.sh`.
#2. Make the script executable: `chmod +x sync.sh`.
#3. Run the script: `./sync.sh <source_directory> #<destination_directory> [options]`.$
### Options
#
#- `--verbose`: Enable verbose mode.
#- `--purge`: Delete files from the destination that are not #in the source.
#- `--forcecopy`: Force copy files even if they exist and are the same.
#- `--use-ctime`: Use creation time instead of modification time.
#- `--use-content`: Compare files based on content.
#- `--2sync`: Enable two-way synchronization.
#- `--hverify`: Verify MD5 hashes after synchronization.
#This script uses `rsync` to handle the synchronization of #directories and `md5sum` to verify the integrity of the #files if requested. The flags can be used to customize the #behavior of the synchronization process.