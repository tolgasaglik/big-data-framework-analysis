import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

DATAFILENAME = "hadoop-records.csv"
QUERY = "real   "
QUERY2 = "user  "
LEN = len(QUERY)
LEN2 = len(QUERY2)


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
    directory = os.fsencode("./experiment2-results")
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
                time = content[index[0]][LEN:-3]
                time2 = content[index2[0]][LEN2:-3]
                jobTIMEarray.append(time)
                jobTIMEarray2.append(time)
                print(jobID+","+str(ntasks[counter//noe])+","+str(time)+","+str(time2))
                DATAFILE.write(jobID+","+str(ntasks[counter//noe])+","+str(time)+","+str(time2)+"\n")
            counter += 1
    DATAFILE.close()


def hadoop_comp_times_plot():
    df = pd.read_csv(DATAFILENAME, sep=',', header=None)
    average = df[1]
    std = df[2]
    plt.bar(df[0], average, width=0.35, yerr=std)
    plt.xticks(df[0], rotation='horizontal')
    plt.title("Hadoop Computation Times")
    plt.xlabel("Nodes X Workers-per-Node")
    plt.ylabel("Elapsed Time(s)")
    dir = "./plots"
    plot_name = "hadoop_comp_times.png"
    filepath = os.path.join(dir, plot_name)
    plt.savefig(filepath, dpi=500)
    plt.show()
    plt.clf()


def hadoop_throughput():
    DataInMB = 102400
    df = pd.read_csv(DATAFILENAME, sep=',', header=None)
    std = DataInMB*df[2]/(df[1]**2)
    df[1] = df[1].apply(lambda x: DataInMB / x)
    df.plot(y=[1], kind='bar', color="red", label=["Megabytes/second"], yerr=std)
    plt.xlabel("Nodes X Workers-per-Node")
    plt.ylabel("Throughput(Mb/s)")
    plt.title("Hadoop Throughput")
    plt.xticks(df.index, df[0], rotation='horizontal')
    dir = "./plots"
    plot_name = "hadoop-throughput.png"
    filepath = os.path.join(dir, plot_name)
    plt.savefig(filepath, dpi=500)
    plt.show()
    plt.clf()


def hadoop_throughput_per_worker():
    DataInMB = 102400
    nWorkers = [2, 3, 4, 6, 8, 9, 12, 12, 16]
    df = pd.read_csv(DATAFILENAME, sep=',', header=None)
    std = DataInMB * df[2] / (df[1] ** 2 * nWorkers)
    df[1] *= nWorkers
    df[1] = df[1].apply(lambda x: DataInMB / x)
    df.plot(y=[1], kind='bar', color="orange", label=["Megabytes/second"], yerr=std)
    plt.xlabel("Nodes X Workers-per-Node")
    plt.ylabel("Throughput(Mb/s)")
    plt.title("Hadoop Throughput per Worker")
    plt.xticks(df.index, df[0], rotation='horizontal')
    dir = "./plots"
    plot_name = "hadoop-throughput-pw.png"
    filepath = os.path.join(dir, plot_name)
    plt.savefig(filepath, dpi=500)
    plt.show()
    plt.clf()


def sparkVShadoop():
    DataInMB = 102400
    sparkDATA = "../Spark-Terasort/experiment-data.csv"
    hadoopDATA = "./hadoop.csv"
    df = pd.read_csv(sparkDATA, sep=',', header=None)
    df2 = pd.read_csv(hadoopDATA, sep=',', header=None)
    average = df.groupby(1, as_index=False).agg({2: "mean", 3: "mean"})
    std = df.groupby(1, as_index=False).agg({2: "std", 3: "std"})
    average[3] = df2[1]
    length = average[1].count()
    x = []
    for i in range(length):
        x.append(average[1][i])
    average.plot(y=[3, 2], kind='bar', label=["Hadoop", "Spark"], yerr=[df2[2], std[2]])
    plt.title("Runtime Comparison")
    plt.xticks(average.index, x, rotation='horizontal')
    plt.xlabel("Nodes X Workers per Node")
    plt.ylabel("Computation Time(s)")
    dir = "./plots"
    plot_name = "sparkVShadoop.png"
    filepath = os.path.join(dir, plot_name)
    plt.savefig(filepath, dpi=500)
    plt.show()
    plt.clf()


def sparkVShadoop_throughput():
    DataInMB = 102400
    sparkDATA = "../Spark-Terasort/experiment-data.csv"
    hadoopDATA = "./hadoop.csv"
    df = pd.read_csv(sparkDATA, sep=',', header=None)
    df2 = pd.read_csv(hadoopDATA, sep=',', header=None)
    average = df.groupby(1, as_index=False).agg({2: "mean", 3: "mean"})
    std = df.groupby(1, as_index=False).agg({2: "std", 3: "std"})
    average[3] = DataInMB/df2[1]
    std2 = DataInMB * std[2] / average[2] ** 2
    average[2] = average[2].apply(lambda x: DataInMB / x)
    length = average[1].count()
    x = []
    for i in range(length):
        x.append(average[1][i])
    average.plot(y=[3, 2], kind='bar', label=["Hadoop", "Spark"], yerr=[(DataInMB*df2[2]/df2[1]**2), std2])
    plt.title("Throughput Comparison")
    plt.xticks(average.index, x, rotation='horizontal')
    plt.xlabel("Nodes X Workers per Node")
    plt.ylabel("Throughput(Mb/s)")
    dir = "./plots"
    plot_name = "sparkVShadoop-tp.png"
    filepath = os.path.join(dir, plot_name)
    plt.savefig(filepath, dpi=500)
    plt.show()
    plt.clf()


def sparkVShadoop_throughput_per_worker():
    DataInMB = 102400
    nWorkers = [2, 3, 4, 6, 8, 9, 12, 12, 16]
    hadoopDATA = "./hadoop.csv"
    sparkDATA = "../Spark-Terasort/experiment-data.csv"
    df = pd.read_csv(sparkDATA, sep=',', header=None)
    df2 = pd.read_csv(hadoopDATA, sep=',', header=None)
    average = df.groupby(1, as_index=False).agg({2: "mean", 3: "mean"})
    std = df.groupby(1, as_index=False).agg({2: "std", 3: "std"})
    average[3] = DataInMB / (df2[1] * nWorkers)
    std2 = DataInMB * std[2] / average[2] ** 2
    average[2] *= nWorkers
    average[2] = average[2].apply(lambda x: DataInMB / x)
    length = average[1].count()
    x = []
    for i in range(length):
        x.append(average[1][i])
    std_hadoop = DataInMB * df2[2] / (df2[1] ** 2 * nWorkers)
    average.plot(y=[3, 2], kind='bar', label=["Hadoop", "Spark"], yerr=[std_hadoop, std2/nWorkers])
    plt.title("Throughput per Worker Comparison")
    plt.xticks(average.index, x, rotation='horizontal')
    plt.xlabel("Nodes X Workers per Node")
    plt.ylabel("Throughput(Mb/s)")
    dir = "./plots"
    plot_name = "sparkVShadoop-tp-pw.png"
    filepath = os.path.join(dir, plot_name)
    plt.savefig(filepath, dpi=500)
    plt.show()
    plt.clf()


if __name__ == '__main__':
    data_generate()
    hadoop_comp_times_plot()
    hadoop_throughput()
    hadoop_throughput_per_worker()
    sparkVShadoop()
    sparkVShadoop_throughput()
    sparkVShadoop_throughput_per_worker()