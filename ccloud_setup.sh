# ccloud CLI setup - Agent-Ready tool
# This shows how agent uses ccloud CLI to manage CockroachDB Cloud control plane

# Install ccloud CLI
# curl https://binaries.cockroachdb.com/ccloud/install.sh | bash

# Auth (agent does this via service account)
ccloud auth login --token $CCLOUD_SERVICE_ACCOUNT_TOKEN --json

# Provision cluster - agent can do this directly, JSON output on every command
ccloud cluster create shadow-memory \
  --cloud aws \
  --region us-west-2 \
  --nodes 3 \
  --type basic \
  --json > cluster.json

# Get connection string - secure, RBAC
ccloud cluster connection-string create shadow-memory --json > conn.json

# Monitor audit logs - agent monitors its own actions
ccloud cluster audit-logs list shadow-memory --json | jq '.logs[] | select(.action=="query")'

# Manage backups - production readiness
ccloud cluster backup create shadow-memory --json

# Networking - secure by default
ccloud cluster networking allowlist create shadow-memory --cidr 0.0.0.0/0 --json

# Example JSON output handling in Python (agent-ready)
# import subprocess, json
# result = subprocess.run(["ccloud", "cluster", "list", "--json"], capture_output=True, text=True)
# clusters = json.loads(result.stdout)
