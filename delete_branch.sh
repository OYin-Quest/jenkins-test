#!/bin/bash
# Author: Ocean Yin
# Run the file in Git Bash under target repository location

SOURCE="${BASH_SOURCE[0]}"
DIR="$( dirname "$SOURCE" )"

input="$DIR/branch.txt"

while read -r line || [ -n  "$line" ];
do
	printf "\n$line Deleting remote tag...\n"
	git tag -l | grep $line | xargs git push origin --delete tag
	
	printf "\n$line Deleting local tag...\n"
	git tag -l | grep $line | xargs git tag -d
	
	printf "\n$line Deleting remote branch...\n"
	git push origin --delete $line
	
	printf "\n$line Deleting local branch...\n"
	git branch -d $line
done < "$input"