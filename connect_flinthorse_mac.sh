#!/bin/bash
# ShadowSense - Connect to CockroachDB Cloud
# Cluster: flint-horse - Agent-ready connection

# Download CA cert for secure connection
curl --create-dirs -o $HOME/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/9be6d061-.../cert'

# DATABASE_URL must be set in env - never hardcode password
# export DATABASE_URL="postgresql://user:pass@host:26257/shadow-memory?sslmode=verify-full"
psql $DATABASE_URL -c "SELECT now();"
psql $DATABASE_URL -f sql/schema.sql
