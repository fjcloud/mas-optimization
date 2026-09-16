# MAS VPA on ROSA HCP

Install the Red Hat Vertical Pod Autoscaler and print Maximo **recommendations**.
VPA does not resize pods. You apply the CR patches yourself.

```bash
pip install -r requirements.txt
ansible-playbook install-vpa.yml
ansible-playbook ensure-vpas.yml
ansible-playbook print-recommendations.yml
```

## Optional: 24h benchmark

```bash
oc new-project mas-vpa-bench

oc create secret generic mas-vpa-bench-creds \
  --from-literal=USER_PASSWORD='LoadTest!Pass001'

oc new-app ./benchmark --name=mas-vpa-bench --strategy=docker \
  -e MAS_DOMAIN=mas1.apps.rosa.fja-hcp.bq37.p3.openshiftapps.com \
  -e MAS_WORKSPACE=ws1

oc set env deploy/mas-vpa-bench --from=secret/mas-vpa-bench-creds
oc rollout status deploy/mas-vpa-bench

oc exec deploy/mas-vpa-bench -- \
  /bin/sh -c 'nohup /opt/benchmark/run.sh 86400 >/tmp/bench.out 2>&1 &'
```
