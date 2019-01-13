import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib import style


QUERY = "DAGScheduler:54 - Job 0 finished: runJob at SparkHadoopWriter.scala:78, took "
LEN = len("yyyy-mm-dd hh:mm:ss INFO  DAGScheduler:54 - Job 0 finished: runJob at SparkHadoopWriter.scala:78, took ")
DATAFILE = open("experiment-data.csv", "w+")


def main():
	jobIDarray = []
	jobNTASKSarray = []
	jobTIMEarray = []
	ntasks = [2,3,4,6,8,9,12,12,16]
	counter = 0
	noe = 30
	directory = os.fsencode(".")
	for file in os.listdir(directory):
		filename = os.fsdecode(file)
		if str(filename[0:15]) == "result_Spark-23":
			print(filename[0:15])
			counter += 1
			jobID = filename[13:19]
			print(jobID)
			jobIDarray.append(jobID)
			jobNTASKSarray.append(ntasks[counter//noe])
			with open(filename) as f:
				content = f.readlines()
			index = [x for x in range(len(content)) if QUERY in content[x]]
			f.close()
			if index:
				time = content[index[0]][LEN:-3]
				jobTIMEarray.append(time)
				print(jobID+","+str(ntasks[counter//noe])+","+str(time))
				DATAFILE.write(jobID+","+str(ntasks[counter//noe])+","+str(time)+"\n")
	DATAFILE.close()


if __name__ == '__main__':
	main()
