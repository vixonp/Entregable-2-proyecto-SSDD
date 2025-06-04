# Dockerfile.pig

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# --- 1. INSTALACIÓN DE PRERREQUISITOS Y JAVA ---
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk wget curl net-tools openssh-server openssh-client rsync && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# --- 2. INSTALACIÓN DE HADOOP ---
ENV HADOOP_VERSION 3.3.6
ENV HADOOP_HOME /opt/hadoop
ENV HADOOP_CONF_DIR /opt/hadoop/etc/hadoop

RUN wget https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -xzf hadoop-$HADOOP_VERSION.tar.gz -C /opt && \
    mv /opt/hadoop-$HADOOP_VERSION $HADOOP_HOME && \
    rm hadoop-$HADOOP_VERSION.tar.gz

ENV PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH

# Configurar SSH para Hadoop (necesario para start-dfs.sh/start-yarn.sh)
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys

# --- 3. CONFIGURACIÓN BÁSICA DE HADOOP
# Copiar las configuraciones
COPY hadoop_conf/core-site.xml $HADOOP_CONF_DIR/
COPY hadoop_conf/hdfs-site.xml $HADOOP_CONF_DIR/
COPY hadoop_conf/mapred-site.xml $HADOOP_CONF_DIR/
COPY hadoop_conf/yarn-site.xml $HADOOP_CONF_DIR/
COPY hadoop_conf/hadoop-env.sh $HADOOP_CONF_DIR/

# Directorios de datos para HDFS
RUN mkdir -p /tmp/hadoop-hdfs/dfs/name && \
           mkdir -p /tmp/hadoop-hdfs/dfs/data && \
           mkdir -p /tmp/hadoop-yarn/yarn/container

# Formatear el NameNode (se hará en el script de inicio o al lanzar el contenedor)
# RUN hdfs namenode -format -force # NO HACER AQUÍ, hacerlo en el script de inicio

# --- 4. INSTALACIÓN DE PIG ---
ENV PIG_VERSION 0.17.0
ENV PIG_HOME /opt/pig

RUN wget https://archive.apache.org/dist/pig/pig-$PIG_VERSION/pig-$PIG_VERSION.tar.gz && \
    tar -xzf pig-$PIG_VERSION.tar.gz -C /opt && \
    mv /opt/pig-$PIG_VERSION $PIG_HOME && \
    rm pig-$PIG_VERSION.tar.gz

ENV PATH=$PIG_HOME/bin:$PATH

# --- 5. DIRECTORIO DE TRABAJO Y SCRIPT DE INICIO ---
# Directorio de trabajo donde se mapeará el volumen ./data
RUN mkdir /data
WORKDIR /data

# Copiar el script de inicio del contenedor (para levantar Hadoop y Pig)
COPY start_hadoop.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start_hadoop.sh

# Puerto de HDFS NameNode (9870), YARN ResourceManager (8088), SSH (22)
EXPOSE 9870 8088 22

# Comando principal al iniciar el contenedor
CMD ["/usr/local/bin/start_hadoop.sh"]