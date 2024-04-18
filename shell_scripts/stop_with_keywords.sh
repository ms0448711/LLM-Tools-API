#!/bin/bash

# The keyword to search for
pipename=$1
keyword=$2
timeout=$3
stop_word=$(date +%s)q7a4z1$(date +%s)
{
  start_time=$(date +%s)
  current_time=$start_time
  while [ $((current_time-start_time)) -le $timeout ]; do
    sleep 1
    current_time=$(date +%s)
  done
  echo $stop_word > $pipename;
} &
pid=$!

# Read each line from the named pipe
while IFS= read -r line; do
  if [[ "$line" != "$stop_word" ]]; then
    echo "$line" # Process the line (for example, by echoing it)
  fi
  # Check if the line contains the keyword
  if echo "$line" | grep -q "$keyword"; then
    #echo "Keyword '$keyword' found. Stopping."
    break # Exit the loop, effectively stopping the reading from the named pipe
  fi
  if echo "$line" | grep -q "$stop_word"; then
    break
  fi
done < "$pipename" # Redirect the input from the named pipe

if ps -a | awk '{print $1}' | egrep -q '^'$pid; then
  kill $pid
fi
 