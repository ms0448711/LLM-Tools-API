#!/bin/bash

# The keyword to search for
keyword=$2
pipename=$1
timeout=$3

start_time=$(date +%s)
read_timeout=$timeout
# Read each line from the named pipe
while IFS= read -r -t $read_timeout line; do
  echo "$line" # Process the line (for example, by echoing it)

  current_time=$(date +%s)
  elapsed_time=$((current_time - start_time))
  if [[ $elapsed_time -ge $timeout ]]; then
    echo "Timeout of $timeout seconds reached. Stopping."
    break
  fi
  # Adjust read_timeout
  if [[ 5 -ge $(($timeout-$elapsed_time))]]; then
    read_timeout=5
  else
    read_timeout=$(($timeout-$elapsed_time))
  fi
  # Check if the line contains the keyword
  if echo "$line" | grep -q "$keyword"; then
    #echo "Keyword '$keyword' found. Stopping."
    break # Exit the loop, effectively stopping the reading from the named pipe
  fi
done < "$pipename" # Redirect the input from the named pipe