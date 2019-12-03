#!/bin/bash
# Author: Ocean Yin
# Run the file in Git Bash under target repository location

SOURCE="${BASH_SOURCE[0]}"
DIR="$( dirname "$SOURCE" )"

input="$DIR/tag.txt"

while IFS=$'\r' read line || [ -n  "$line" ];
do
	printf "\n$line Deleting remote tag...\n"
	git push origin --delete $line
	
	printf "\n$line Deleting local tag...\n"
	git tag -d $line
done < "$input"