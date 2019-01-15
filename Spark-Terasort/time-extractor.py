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
    ntasks = [2,3,4,6,8,9,12,12.1,16]
    ntasks =["1x2","1x3","1x4","2x3","2x4","3x3","3x4","4x3","4x4"]
    counter = 0
    noe = 30
    directory = os.fsencode("./experiment-results")
    for file in sorted(os.listdir(directory)):
        filename = os.fsdecode(file)
        if str(filename[0:13]) == "result_Spark-":
            #print(filename[0:13])
            jobID = filename[13:19]
            #print(jobID)
            jobIDarray.append(jobID)
            jobNTASKSarray.append(ntasks[counter//noe])
            filepath = os.path.join(directory, file)
            with open(filepath) as f:
                content = f.readlines()
            index = [x for x in range(len(content)) if QUERY in content[x]]
            f.close()
            if index:
                time = content[index[0]][LEN:-3]
                jobTIMEarray.append(time)
                print(jobID+","+str(ntasks[counter//noe])+","+str(time))
                DATAFILE.write(jobID+","+str(ntasks[counter//noe])+","+str(time)+"\n")
            counter += 1
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
    plt.plot(x, y, '-')
    plt.xticks(x)
    plt.title("TeraSort Computation Times")
    plt.xlabel("Nodes x Task-per-Node")
    plt.ylabel("Elapsed Time(s)")
    #plt.legend(legend_list, loc='upper right')
    dir = "./plots"
    plot_name = "spark-terasort.png"
    filepath = os.path.join(dir, plot_name)
    plt.savefig(filepath, dpi=500)
    #plt.show()
    plt.clf()


if __name__ == '__main__':
    #data_generate()
    data_plot()
