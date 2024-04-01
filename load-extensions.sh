#!/bin/sh
set -e

echo "Running Postgres extensions script"

for extension in `cat /tmp/postgres_extensions.txt`; do
	for tpl in template1; do
		psql --username "$POSTGRES_USER" -d $tpl -c "CREATE EXTENSION IF NOT EXISTS ${extension};"
	done
done
