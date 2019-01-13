import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib import style


QUERY = "DAGScheduler:54 - Job 0 finished: runJob at SparkHadoopWriter.scala:78, took "
LEN = len("yyyy-mm-dd hh:mm:ss INFO  DAGScheduler:54 - Job 0 finished: runJob at SparkHadoopWriter.scala:78, took ")
DATAFILENAME = "experiment-data.csv"


def data_generate():
    DATAFILE = open(DATAFILENAME, "w+")
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
            #print(filename[0:15])
            counter += 1
            jobID = filename[13:19]
            #print(jobID)
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

def data_plot():
    #my_data = np.genfromtxt(DATAFILENAME, delimiter=',')
    df = pd.read_csv(DATAFILENAME, sep=',', header=None)
    #average = df.groupby(1)[2].mean()
    average = df.groupby(1, as_index=False).agg({2: "mean"})
    length = average[1].count()
    x=[]
    y=[]
    for i in range(length):
        x.append(average[1][i])
        y.append(average[2][i])
    plt.plot(x, y ,'-')
    plt.xticks(x)
    plt.title("TeraSort Computation Times")
    plt.xlabel("Number of Tasks in Parallel")
    plt.ylabel("Computation Time(s)")
    #plt.legend(legend_list, loc='upper right')
    plt.savefig('plots/spark-terasort.png', dpi=500)
    #plt.show()
    plt.clf()


if __name__ == '__main__':
    data_generate()
    data_plot()
