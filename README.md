# MAS VPA on ROSA HCP

Right-size IBM Maximo Application Suite with the **Red Hat** Vertical Pod
Autoscaler. VPA only **recommends**. You copy `target` onto IBM custom
resources. Pods are never auto-resized.

```
oc apply -k deploy          # operator + controller + Off-mode VPAs
ansible-playbook print-recommendations.yml
```

`ansible-playbook` uses the `oc` login of the current shell.

## What gets applied

`deploy/` is one Kustomize directory:

| File | Resource |
|------|----------|
| `operator.yaml` | Namespace, OperatorGroup, Subscription (`redhat-operators`, **worker** nodeSelector) |
| `controller.yaml` | `VerticalPodAutoscalerController` pinned to workers, `recommendationOnly: true` |
| `vpas-off.yaml` | Off-mode VPAs for MAS Core, Manage bundles, and Db2 |

ROSA hosted control plane has no schedulable masters. Without the worker
selector the operator stays Pending.

On a **new** cluster the VPA CRDs appear only after the CSV is Succeeded. If
the first apply reports `no matches for kind VerticalPodAutoscaler`, wait and
run the same command again:

```bash
oc apply -k deploy
oc wait csv -n openshift-vertical-pod-autoscaler \
  -l operators.coreos.com/vertical-pod-autoscaler.openshift-vertical-pod-autoscaler \
  --for=jsonpath='{.status.phase}'=Succeeded --timeout=300s
oc apply -k deploy
```

## Rules

1. Every MAS VPA stays `updateMode: Off`. Never Auto / Recreate / Initial.
2. Patch CRs, not Deployments:
   - Core → `Suite.spec.podTemplates`
   - Manage JVM → `ManageWorkspace.spec.settings.resources.serverBundles` (one pair for every bundle; take the **max** VPA target, usually ui)
   - Db2 → `Db2uCluster.spec.podConfig.db2u.resource.db2u`
3. Red Hat catalog only. No anyuid SCC.
4. Do not shrink Db2 memory below live RSS.
5. Prefer a 24h recommendation window. Do not copy a short-history `upperBound` onto limits.

Manage sidecars (`monitoragent`) are opted out in `vpas-off.yaml`. Names assume instance `mas1` / workspace `ws1`.

## After apply

```bash
oc get pods -n openshift-vertical-pod-autoscaler -o wide
oc get vpa -A -l app.kubernetes.io/part-of=mas-vpa-off \
  -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,MODE:.spec.updatePolicy.updateMode,TARGET:.spec.targetRef.name
ansible-playbook print-recommendations.yml
```

Then patch the IBM CRs with the `target` values. Dry-run first (`--dry-run=server`). Confirm Suite / Manage / Db2 Ready after the operator rolls the pods.

Docs: [OpenShift VPA (Off mode)](https://docs.okd.io/4.22/nodes/pods/nodes-pods-vertical-autoscaler.html).
