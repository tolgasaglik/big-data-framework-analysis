#!/bin/bash -l
# Time-stamp: <Thu 2019-01-24 15:33 svarrette>
##################################################################
# Generic Hadoop/Flink standalone cluster
##################################################################
#SBATCH -J Hadoop34
#SBATCH --time=0-01:00:00   # 1 hour
#SBATCH --partition=batch
#SBATCH --qos qos-batch
###SBATCH -N 3
###SBATCH --ntasks-per-node=1
### -c, --cpus-per-task=<ncpus>
###     (multithreading) Request that ncpus be allocated per process
#SBATCH -c 6
#SBATCH --exclusive
###SBATCH --mem=0
#SBATCH --dependency=singleton
### Guess the run directory
# - either the script directory upon interactive jobs
# - OR the submission directory upon passive/batch jobs
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -n "${SLURM_SUBMIT_DIR}" ]; then
    [[ "${SCRIPTDIR}" == *"slurmd"* ]] && RUNDIR=${SLURM_SUBMIT_DIR} || RUNDIR=${SCRIPTDIR}
else
    RUNDIR=${SCRIPTDIR}
fi

############################################
################# Let's go #################
############################################
# Use the RESIF build modules
if [ -f  /etc/profile ]; then
    .  /etc/profile
fi

# Parse the command-line argument
while [ $# -ge 1 ]; do
    case $1 in
        -h | --help)  usage;   exit 0;;
        -a | --all)   SETUP_HADOOP="$1";  SETUP_FLINK="$1";;
        --hadoop)     SETUP_HADOOP="$1";;
        --flink)      SETUP_FLINK="$1";;
    esac
    shift
done


### General SLURM Parameters
echo "SLURM_JOBID  = ${SLURM_JOBID}"
echo "SLURM_JOB_NODELIST = ${SLURM_JOB_NODELIST}"
echo "SLURM_NNODES = ${SLURM_NNODES}"
echo "SLURM_NTASK  = ${SLURM_NTASKS}"
echo "Submission directory = ${SLURM_SUBMIT_DIR}"

# Load local Spark module
module purge || print_error_and_exit "Unable to find the 'module' command"
module use $HOME/.local/easybuild/modules/all

[ -n "${SETUP_HADOOP}" ] && module load lang/Java
[ -n "${SETUP_FLINK}"  ] && module load devel/Flink

export HADOOP_HOME="/home/users/@USER/.local/lib/hadoop-2.7.5"
export FLINK_HOME=$EBROOTFLINK


CONFDIR=${RUNDIR}/job-${SLURM_JOBID}/conf

if [ ! -d "${CONFDIR}" ]; then
    echo "=> creating ${CONFDIR}"
    mkdir -p ${CONFDIR}
fi

if [ -z "$data_dir" ]; then
    #echo "*** ERROR *** --data-dir not given" >&2
    #exit 1
    data_dir="$PWD"
fi

if [ -z "$hadoop_dir" ]; then
    if [ -n "$HADOOP_HOME" ]; then
        hadoop_dir="$HADOOP_HOME"
    else
        echo "*** ERROR *** --hadoop-dir not given and \$HADOOP_HOME not set" >&2
        exit 1
    fi
fi

hadoop_tmp_dir="/home/users/$USER/hadoop"
if echo "$hadoop_tmp_dir" | grep -q "'"; then
    echo "*** ERROR *** hadoop_tmp_dir cannot contain single quotes" >&2
    exit 1
fi

export MASTER=$(scontrol show hostname $SLURM_NODELIST | head -n 1)
### Populate confdir
# generate master file containing the 1st node reserved
if [ ! -f "${CONFDIR}/master" ]; then
    echo $MASTER > ${CONFDIR}/master
fi
# remaining nodes are set to slaves
if [ ! -f "${CONFDIR}/slaves" ]; then
    scontrol show hostname $SLURM_NODELIST | tail -n $(echo "$SLURM_NNODES-1" | bc) > ${CONFDIR}/slaves
fi


#--- find some free ports

#note the available port range
read pmin pmax < /proc/sys/net/ipv4/ip_local_port_range

#hash this job's unique id to get a 32-bit number (8 hex digits)
hash32=$(echo "$jobidstr" | md5sum | awk '{print substr($1,0,8)}')

#use the hash to pick a starting point in the bottom half of the available range
pmin=$(( $pmin + 0x$hash32 % (($pmax - $pmin)/2) ))

#JobTracker
#log "search for a free port for the JobTracker to use, starting at port $pmin"
#if ! job_tracker_port="$(free_port "$pmin" "$pmax")"; then
#    echo "*** ERROR *** unable to find a free port between $pmin and $pmax" >&2
#    exit 1
#fi
#log "using JobTracker port $job_tracker_port"
#pmin=$(( $job_tracker_port + 1 ))

#JobTracker http
#log "search for a free port for the JobTracker http to use, starting at port $pmin"
#if ! job_tracker_http_port="$(free_port "$pmin" "$pmax")"; then
#    echo "*** ERROR *** unable to find a free port between $pmin and $pmax" >&2
#    exit 1
#fi
#log "using JobTracker http port $job_tracker_http_port"
#pmin=$(( $job_tracker_http_port + 1 ))

#TaskTracker http
#log "search for a free port for the TaskTracker http to use, starting at port $pmin"
#if ! task_tracker_http_port="$(free_port "$pmin" "$pmax")"; then
#    echo "*** ERROR *** unable to find a free port between $pmin and $pmax" >&2
#    exit 1
#fi
#log "using TaskTracker http port $task_tracker_http_port"
#pmin=$(( $task_tracker_http_port + 1 ))


if [ -n "${SETUP_FLINK}" ]; then
    echo "==> setup Flink configuration"
    cp $FLINK_HOME/conf/flink-conf.yaml ${CONFDIR}/
    echo " -> adapting ${CONFDIR}/flink-conf.yaml"
    echo "    setting jobmanager.rpc.address:  $MASTER"
    sed -i -e \
        "s/^[[:space:]]*jobmanager\.rpc\.address: .*/jobmanager\.rpc\.address: $MASTER/" ${CONFDIR}/flink-conf.yaml
     # [...] Hotel transilvania

fi









if [ -n "${SETUP_HADOOP}" ]; then
    echo "==> setup Hadoop configuration"
    echo " -> copy /home/users/@USER/.local/lib/hadoop-2.7.5/etc/hadoop/*.xml"
    cp /home/users/$USER/.local/lib/hadoop-2.7.5/etc/hadoop/*.xml ${CONFDIR}/
    #core conf
    cat > ${CONFDIR}/core-site.xml <<EOF
    <?xml version="1.0"?> 
    <?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
    <!-- Put site-specific property overrides in this file. -->
    <configuration>
        <property>
            <name>hadoop.tmp.dir</name>
            <value>$hadoop_tmp_dir</value>
        </property>
        <property>
            <name>fs.default.name</name>
            <value>file://$data_dir</value>
        </property>
    </configuration>
EOF

    #mapred conf
    cat > ${CONFDIR}/mapred-site.xml <<EOF
    <?xml version="1.0"?>
    <?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
    <!-- Put site-specific property overrides in this file. -->
    <configuration>
         <property>
            <name>mapred.system.dir</name>
            <value>\${fs.default.name}/hadoop/mapred/system</value>
        </property>
        <property>
            <name>mapreduce.jobtracker.staging.root.dir</name>
            <value>\${fs.default.name}/hadoop/mapred/staging</value>
        </property>
        <property>
            <name>mapred.tasktracker.map.tasks.maximum</name>
            <value>$max_tasks_per_host</value>
        </property>
        <property>
            <name>mapred.tasktracker.reduce.tasks.maximum</name>
            <value>$max_tasks_per_host</value>
        </property>
    </configuration>
EOF

time hadoop jar ~/.local/lib/hadoop-2.7.5/share/hadoop/mapreduce/hadoop-*example*.jar  terasort ~/bigdatahadoop/input $SCRATCH/output34 >> log-${SLURM_NNODES}-${SLURM_NNTASKS}
rm -r $SCRATCH/output34


 fi
