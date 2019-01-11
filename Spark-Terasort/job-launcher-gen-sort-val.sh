#!/bin/bash -l

rm -r $HOME/data
echo "Running benchmark with 1 nodes and 2 tasks" 
sbatch -N 1 --ntasks-per-node=2 spark-teralauncher.sh
for n in {1..4}
do
	for t in {3..4}
	do
		rm -r $HOME/data
		echo "Running benchmark with ${n} nodes and ${t} tasks" 
		sbatch -N ${n} --ntasks-per-node=${t} spark-teralauncher.sh
	done
done
