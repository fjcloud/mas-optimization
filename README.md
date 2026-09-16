# MAS VPA on ROSA HCP

Install the Red Hat Vertical Pod Autoscaler, read its **recommendations**, then
copy those numbers onto IBM Maximo CRs yourself. VPA never resizes pods
(`updateMode: Off`).

```bash
pip install -r requirements.txt
ansible-galaxy collection install kubernetes.core
oc apply -k deploy
ansible-playbook print-recommendations.yml
```

The playbook uses `kubernetes.core.k8s_info` and the kubeconfig from this shell.

On a brand-new cluster the CRDs are not there yet. If apply fails with
`no matches for kind VerticalPodAutoscaler`, wait a minute and run
`oc apply -k deploy` again.

## `deploy/`

| File | Role |
|------|------|
| `operator.yaml` | Red Hat VPA Operator, scheduled on **workers** (ROSA HCP has no masters) |
| `controller.yaml` | Recommender only (`recommendationOnly: true`) |
| `vpas-off.yaml` | One Off VPA per MAS Core / Manage / Db2 workload (`mas1` / `ws1`) |

## How to use a recommendation

The playbook prints `CURRENT` vs VPA `TARGET`. If ACTION is **RAISE**, patch
the IBM CR (not the Deployment):

| Component | CR field |
|-----------|----------|
| Manage JVM | `ManageWorkspace.spec.settings.resources.serverBundles` — one request for every bundle; use the **max** target (usually ui) |
| MAS Core | `Suite.spec.podTemplates` (merge replaces the whole list: keep every existing entry) |
| Db2 | `Db2uCluster.spec.podConfig.db2u.resource.db2u` — do not cut memory below live usage |

Leave workloads **in band** alone. Do not copy `UPPER` onto limits.
