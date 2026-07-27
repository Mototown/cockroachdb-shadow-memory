# Mac setup for flint-horse cluster - run in Terminal

# 1. Download CA cert (required only once) - from your screenshot
curl --create-dirs -o $HOME/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/9be6d061-e812-4cdb-8202-123e85d89218/cert'

# 2. Set DATABASE_URL env var (replace <PASSWORD> with the one you sent me)
export DATABASE_URL="postgresql://Moshi:<PASSWORD>@flint-horse-18758.jxf.gcp-us-central1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"

# 3. Test connection
psql $DATABASE_URL -c "SELECT now();"

# 4. Create vector extension + schema for hackathon
psql $DATABASE_URL -f sql/schema.sql

# 5. If you use Python, your code from screenshot works as-is:
# import os
# import psycopg2
# conn = psycopg2.connect(os.environ["DATABASE_URL"])
