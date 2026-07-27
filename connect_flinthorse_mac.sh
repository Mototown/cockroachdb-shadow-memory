curl --create-dirs -o $HOME/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/9be6d061-e812-4cdb-8202-123e85d89218/cert'
export DATABASE_URL="postgresql://Moshi:<PASSWORD>@flint-horse-18758.jxf.gcp-us-central1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"
psql $DATABASE_URL -c "SELECT now();"
psql $DATABASE_URL -f sql/schema.sql
