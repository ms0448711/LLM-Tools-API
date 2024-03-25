#!/bin/bash

# The keyword to search for
keyword=$2
pipename=$1


# Read each line from the named pipe
while IFS= read -r line; do
  echo "$line" # Process the line (for example, by echoing it)

  # Check if the line contains the keyword
  if echo "$line" | grep -q "$keyword"; then
    #echo "Keyword '$keyword' found. Stopping."
    break # Exit the loop, effectively stopping the reading from the named pipe
  fi
done < "$pipename" # Redirect the input from the named pipe