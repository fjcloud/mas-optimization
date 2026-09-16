# MAS VPA on ROSA HCP

Install the Red Hat Vertical Pod Autoscaler, read its **recommendations**, then
patch IBM Maximo CRs yourself. VPA never resizes pods (`updateMode: Off`).

```bash
pip install -r requirements.txt
oc apply -k deploy
ansible-playbook print-recommendations.yml
```

`pip install -r requirements.txt` installs the `ansible` package (it already
includes `kubernetes.core`) and the Kubernetes Python client. No Galaxy step.

On a brand-new cluster the CRDs are not there yet. If apply fails with
`no matches for kind VerticalPodAutoscaler`, wait a minute and run
`oc apply -k deploy` again.

The playbook prints the table, writes merge/JSON patches under `output/`
(gitignored), and prints the `oc patch --patch-file` commands. It does **not**
apply them.

## `deploy/`

| File | Role |
|------|------|
| `operator.yaml` | Red Hat VPA Operator, scheduled on **workers** (ROSA HCP has no masters) |
| `controller.yaml` | Recommender only (`recommendationOnly: true`) |
| `vpas-off.yaml` | One Off VPA per MAS Core / Manage workload (`mas1` / `ws1`). Db2 is out of scope. |

## Patches

| File | Type | What it changes |
|------|------|-----------------|
| `output/manageworkspace-serverbundles.yaml` | merge | `ManageWorkspace` `spec.settings.resources.serverBundles.requests` only (max of bundle targets) |
| `output/suite-podtemplates.yaml` | json | individual `Suite.spec.podTemplates[i].containers[j].resources.requests` keys |

Leave **in-band** workloads alone. Do not copy `UPPER` onto limits. Db2 is not recommended or patched.
