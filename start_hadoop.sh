#!/bin/bash

echo "Starting Hadoop services..."

# Set required environment variables
export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root
export HDFS_SECONDARYNAMENODE_USER=root
export YARN_RESOURCEMANAGER_USER=root
export YARN_NODEMANAGER_USER=root

# Format only once
if [ ! -f /tmp/hadoop-hdfs/dfs/name/current/VERSION ]; then
    echo "Formateando HDFS NameNode..."
    hdfs namenode -format
else
    echo "HDFS NameNode ya formateado."
fi

# Start HDFS daemons sin SSH
echo "Iniciando HDFS..."
$HADOOP_HOME/bin/hdfs --daemon start namenode
$HADOOP_HOME/bin/hdfs --daemon start datanode
$HADOOP_HOME/bin/hdfs --daemon start secondarynamenode

# Start YARN daemons sin SSH
echo "Iniciando YARN..."
$HADOOP_HOME/bin/yarn --daemon start resourcemanager
$HADOOP_HOME/bin/yarn --daemon start nodemanager

# Mostrar procesos de Hadoop
jps

echo "Hadoop services started. Keeping container alive..."
tail -f /dev/null
