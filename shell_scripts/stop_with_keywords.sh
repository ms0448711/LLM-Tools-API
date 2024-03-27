#!/bin/bash

# The keyword to search for
pipename=$1
keyword=$2
timeout=$3
{
  start_time=$(date +%s)
  current_time=$start_time
  while [ $((current_time-start_time)) -le $timeout ]; do
    sleep 1
    current_time=$(date +%s)
  done
  echo $keyword > $pipename;
} &
pid=$!

# Read each line from the named pipe
while IFS= read -r line; do
  echo "$line" # Process the line (for example, by echoing it)
  
  # Check if the line contains the keyword
  if echo "$line" | grep -q "$keyword"; then
    #echo "Keyword '$keyword' found. Stopping."
    break # Exit the loop, effectively stopping the reading from the named pipe
  fi
done < "$pipename" # Redirect the input from the named pipe

if kill -0 $pid; then
  kill $pid
fi
 