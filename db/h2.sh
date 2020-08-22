#!/bin/sh
dir=$(dirname "$0")
ls -al "$dir/h2-1.4.200.jar"
java -cp ./h2-1.4.200.jar org.h2.tools.Server -webAllowOthers -tcpAllowOthers -tcpPassword admin -webPort 5656 -tcpPort 5454
