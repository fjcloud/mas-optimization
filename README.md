# MAS VPA on ROSA HCP

Install the Red Hat Vertical Pod Autoscaler, read its **recommendations**, then
patch IBM Maximo CRs yourself. VPA never resizes pods (`updateMode: Off`).

```bash
pip install -r requirements.txt
oc apply -k deploy
ansible-playbook ensure-vpas.yml
ansible-playbook print-recommendations.yml
```

`pip install -r requirements.txt` installs the `ansible` package (it already
includes `kubernetes.core`) and the Kubernetes Python client. No Galaxy step.

On a brand-new cluster the CRDs are not there yet. If apply fails with
`no matches for kind VerticalPodAutoscaler`, wait a minute and run
`oc apply -k deploy` again.

`ensure-vpas.yml` creates one Off VPA per MAS workload it finds. A VPA object
cannot select a namespace by label (`targetRef` must name one Deployment), so
the playbook lists IBM labels instead of hard-coding `mas1` / `ws1`:

- Manage JVMs: `mas.ibm.com/appType=serverBundle`
- Core APIs: each `Suite` `spec.podTemplates` entry, plus `licensing-mediator`

`print-recommendations.yml` prints the table, writes merge/JSON patches under
`output/` (gitignored), and prints the `oc patch --patch-file` commands. It
does **not** apply them.

## Optional: 24h IBM Manage soak

VPA recommendations get better after a day of real UI traffic. Do **not** run
JMeter on your laptop. `benchmark/` is an idle pod on the cluster; you exec
the IBM `MAS-Manage-UI` plan when you want.

There is no API. A small REST wrapper would only start the same script. For
24h, start it with `nohup` in the pod and disconnect. Duration is the argument
to `run.sh`, not an env var.

```bash
# from the mas-vpa repo
oc new-project mas-vpa-bench   # skip if you already have a namespace

oc create secret generic mas-vpa-bench-creds \
  --from-literal=USER_PASSWORD='LoadTest!Pass001'

oc new-app ./benchmark --name=mas-vpa-bench --strategy=docker \
  -e MAS_DOMAIN=mas1.apps.rosa.fja-hcp.bq37.p3.openshiftapps.com \
  -e MAS_WORKSPACE=ws1

oc set env deploy/mas-vpa-bench --from=secret/mas-vpa-bench-creds
oc rollout status deploy/mas-vpa-bench

# 24h soak (returns immediately). Summary is in the container logs:
#   oc logs -f deploy/mas-vpa-bench
oc exec deploy/mas-vpa-bench -- \
  /bin/sh -c 'nohup /opt/benchmark/run.sh 86400 >/tmp/bench.out 2>&1 &'
```

Defaults are a light IBM mix (~12 VUs, 15s think) — not month-end. Pass the
run length in seconds to `run.sh` (`600` for ten minutes, `86400` for a day).
Load users (`asset0001`, `wocrt0001`, …) must already exist in MAS. When it
finishes, rerun `ansible-playbook print-recommendations.yml`.

## `deploy/`

| File | Role |
|------|------|
| `operator.yaml` | Red Hat VPA Operator, scheduled on **workers** (ROSA HCP has no masters) |
| `controller.yaml` | Recommender only (`recommendationOnly: true`) |

## Patches

| File | Type | What it changes |
|------|------|-----------------|
| `output/manageworkspace-serverbundles.yaml` | merge | `ManageWorkspace` `spec.settings.resources.serverBundles.requests` only (max of bundle targets) |
| `output/suite-podtemplates.yaml` | json | individual `Suite.spec.podTemplates[i].containers[j].resources.requests` keys |
