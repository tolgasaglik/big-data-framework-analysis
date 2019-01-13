#!/bin/bash -l

echo "Running benchmark with 1 nodes and 2 tasks" 
for i in {1..30}
do
	sbatch -N 1 --ntasks-per-node=2 spark-terasort.sh
done
for n in {1..4}
do
	for t in {3..4}
	do
		echo "Running benchmark with ${n} nodes and ${t} tasks" 
		for i in {1..30}
		do
			sbatch -N ${n} --ntasks-per-node=${t} spark-terasort.sh
		done
	done
done
