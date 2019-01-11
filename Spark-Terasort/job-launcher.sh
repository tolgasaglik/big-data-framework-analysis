#!/bin/bash -l

for n in {1..4}
do
	for t in {3..4}
	do
		echo "Running benchmark with ${n} nodes and ${t} tasks per node" 
		sbatch -N ${n} --ntasks-per-node=${t} spark-teragen.sh
		sleep 5
		sbatch -N ${n} --ntasks-per-node=${t} spark-terasort.sh
		sleep 5
		sbatch -N ${n} --ntasks-per-node=${t} spark-teravalidate.sh
		sleep 5
	done
done
