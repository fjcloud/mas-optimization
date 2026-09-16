# MAS VPA on ROSA HCP

Install the Red Hat Vertical Pod Autoscaler and print Maximo **recommendations**.
VPA does not resize pods. You apply the CR patches yourself.

Requirements: Python, pip, and an `oc` session already logged in to the
OpenShift cluster.

```bash
pip install -r requirements.txt
ansible-playbook vpa.yml
ansible-playbook print-recommendations.yml
```

## Optional: 24h benchmark

```bash
oc new-project mas-vpa-bench

# One Manage user with Start Center, Locations, Purchase Orders, and Work Orders
# (including status changes). Same account is reused by every JMeter thread.
oc create secret generic mas-vpa-bench-creds \
  --from-literal=USERNAME='bench' \
  --from-literal=USER_PASSWORD='ChangeMe'

MANAGE_HOST=$(oc get route -A -l mas.ibm.com/applicationId=manage \
  -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.host}{"\n"}{end}' \
  | awk '$1 ~ /-manage-/ && $1 !~ /-81$/ {print $2; exit}')
MAS_WORKSPACE=${MANAGE_HOST%%.*}
MAS_DOMAIN=${MANAGE_HOST#*.manage.}

oc new-app ./benchmark --name=mas-vpa-bench --strategy=docker \
  -e MAS_DOMAIN="$MAS_DOMAIN" \
  -e MAS_WORKSPACE="$MAS_WORKSPACE"

oc set env deploy/mas-vpa-bench --from=secret/mas-vpa-bench-creds

oc exec deploy/mas-vpa-bench -- \
  /bin/sh -c 'nohup /opt/benchmark/run.sh 86400 >/tmp/bench.out 2>&1 &'
```
