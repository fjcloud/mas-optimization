# MAS optimization on ROSA HCP

Install Red Hat VPA, print Maximo **recommendations**, and optionally rebalance
pods with the descheduler. VPA does not resize pods. You apply the CR patches
yourself.

Requirements: Python, pip, and an `oc` session already logged in to the
OpenShift cluster.

```bash
pip install -r requirements.txt
ansible-playbook vpa.yml
ansible-playbook print-recommendations.yml
```

## Optional: descheduler

Evicts pods from packed workers onto emptier ones; `mas-bench` is never touched.

```bash
ansible-playbook descheduler.yml
```

## Optional: 24h benchmark

IBM JMeter soak against Manage; one user in the secret, reused by every thread (Start Center, Locations, POs, Work Orders including status changes).

```bash
oc new-project mas-bench
oc create secret generic mas-bench-creds \
  --from-literal=USERNAME='bench' \
  --from-literal=USER_PASSWORD='ChangeMe'

oc new-app ./benchmark --name=mas-bench --strategy=docker \
  -e MAS_DOMAIN=mas1.apps.rosa.fja-hcp.bq37.p3.openshiftapps.com \
  -e MAS_WORKSPACE=ws1

oc set env deploy/mas-bench --from=secret/mas-bench-creds

oc exec deploy/mas-bench -- \
  /bin/sh -c 'nohup /opt/benchmark/run.sh 86400 >/tmp/bench.out 2>&1 &'
```
