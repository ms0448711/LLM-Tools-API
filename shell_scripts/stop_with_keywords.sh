#!/bin/bash

# The keyword to search for
keyword=$1

# Read each line from stdin
while IFS= read -r line; do
  echo "$line" # Process the line (for example, by echoing it)

  # Check if the line contains the keyword
  if echo "$line" | grep -q "$keyword"; then
    #echo "Keyword '$keyword' found. Stopping."
    break # Exit the loop, effectively stopping the pipeline
  fi
done