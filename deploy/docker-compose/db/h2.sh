#!/bin/sh
pwd
dir=$(dirname "$0")
echo "dir: ${dir}"
echo "H2DRIVERS: ${H2DRIVERS}"
echo "CLASSPATH: ${CLASSPATH}"
ls -al "$dir/h2-1.4.200.jar"
java -cp ./h2-1.4.200.jar org.h2.tools.Server -webAllowOthers -tcpAllowOthers -tcpPassword admin -webPort 8686 -tcpPort 8787
