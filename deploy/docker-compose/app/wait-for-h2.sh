#!/bin/sh

set -e

host="$1"
shift
user="$1"
shift
password="$1"
shift
cmd="$@"

confirm_sql() {
  >&2 echo "[host] $host, [user] $user"
  java -cp /var/db/h2-1.4.200.jar org.h2.tools.RunScript \
	  -url "jdbc:h2:tcp://${host}//var/db/nuxtboot" \
	  -user ${user} -password ${password} \
	  -script /var/db/connect_confirm.sql \
	  -showResults
  
}


until confirm_sql; do
  >&2 echo "H2 is unavailable - sleeping"
  sleep 1
done

>&2 echo "H2 is up - executing command"
exec $cmd
