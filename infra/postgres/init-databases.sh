#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE bazaar_users;
    CREATE DATABASE bazaar_commerce;
    GRANT ALL PRIVILEGES ON DATABASE bazaar_users TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE bazaar_commerce TO $POSTGRES_USER;
EOSQL
