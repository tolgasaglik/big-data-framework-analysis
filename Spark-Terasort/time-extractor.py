import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib import style
from io import StringIO


QUERY = "DAGScheduler:54 - Job 0 finished: runJob at SparkHadoopWriter.scala:78, took "
QUERY2 = "DAGScheduler:54 - ResultStage 1 (runJob at SparkHadoopWriter.scala:78) finished in "
LEN = len("yyyy-mm-dd hh:mm:ss INFO  DAGScheduler:54 - Job 0 finished: runJob at SparkHadoopWriter.scala:78, took ")
LEN2 = len("yyyy-mm-dd hh:mm:ss INFO  DAGScheduler:54 - ResultStage 1 (runJob at SparkHadoopWriter.scala:78) finished in ")
DATAFILENAME = "experiment-data.csv"


def data_generate():
    DATAFILE = open(DATAFILENAME, "w+")
    jobIDarray = []
    jobNTASKSarray = []
    jobTIMEarray = []
    jobTIMEarray2 = []
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
            index2 = [x for x in range(len(content)) if QUERY2 in content[x]]
            f.close()
            if index:
                time = content[index[0]][LEN:-7]
                time2 = content[index2[0]][LEN2:-4]
                jobTIMEarray.append(time)
                jobTIMEarray2.append(time)
                print(jobID+","+str(ntasks[counter//noe])+","+str(time)+","+str(time2))
                DATAFILE.write(jobID+","+str(ntasks[counter//noe])+","+str(time)+","+str(time2)+"\n")
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
    plt.show()
    plt.clf()


def io_rate_plot():
    df = pd.read_csv(DATAFILENAME, sep=',', header=None)
    average = df.groupby(1, as_index=False).agg({2: "mean", 3: "mean"})
    length = average[1].count()
    x = []
    x2 = []
    for i in range(length):
        x.append(average[1][i])
        x2.append("%.2f" %(average[2][i]/average[3][i]))
    average.plot(y=[2, 3], kind='bar', label=["Write", "Read"])
    plt.title("Spark I/O Rate")
    plt.xticks(average.index, x2)
    plt.show()
    dir = "./plots"
    plot_name = "spark-io-rates.png"
    filepath = os.path.join(dir, plot_name)
    plt.savefig(filepath, dpi=500)
    plt.clf()


def thourghput():
    DataInMB = 102400
    df = pd.read_csv(DATAFILENAME, sep=',', header=None)
    average = df.groupby(1, as_index=False).agg({2: "mean", 3: "mean"})
    length = average[1].count()
    x = []
    for i in range(length):
        x.append(average[1][i])
    average[2] = average[2].apply(lambda x: DataInMB/x)
    average[3] = average[3].apply(lambda x: DataInMB/x)
    average.plot(y=[2, 3], kind='bar', label=["Write", "Read"])
    plt.xlabel("Nodes X Task-per-Node")
    plt.ylabel("Throughput(Mb/s)")
    plt.title("Spark Throughput")
    plt.xticks(average.index, x)
    dir = "./plots"
    plot_name = "spark-throughput.png"
    filepath = os.path.join(dir, plot_name)
    plt.savefig(filepath, dpi=500)
    plt.show()
    plt.clf()


def statistics():
    df = pd.read_csv(DATAFILENAME, sep=',',header=None)
    desc = df[2].groupby(df[1]).describe()
    fig, ax = plt.subplots(figsize=(10, 8))
    plt.suptitle('')
    data.boxplot(column=['SepalLength'], by='Name', ax=ax)
    bp = df.boxplot(column=2, by=1, ax=ax)
    ax.set_xlabel('Nodes X Task-per-Node')
    fig = np.asarray(bp).reshape(-1)[0].get_figure()
    fig.suptitle('Boxplot for Runtimes')
    plt.show()



if __name__ == '__main__':
    data_generate()
    data_plot()
    statistics()
    io_rate_plot()
    thourghput()
