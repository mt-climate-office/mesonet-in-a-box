#!/bin/bash

trap 'rm -f "$TMPFILE"' EXIT

TMPFILE=$(mktemp --suffix .json) || exit 1
# echo "Our temp file is $TMPFILE"

## Get a station's data
cora_cmd \
--echo=on \
--input="{
connect fcfc-mesonet-ln.cfc.umt.edu; 
logger-query-ex ${1} FiveMin $TMPFILE most-recent 3 --format=\"TOACI1\" --reported-station-name=${1};
}"

# Remove first line of tempfile.
sed -i '1d' $TMPFILE
cp $TMPFILE ./ln_out.dat
