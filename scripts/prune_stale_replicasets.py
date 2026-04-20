#!/usr/bin/env python3
"""Prune stale Deployment-owned ReplicaSets to free namespace quota.

Keeps the newest two ReplicaSets per Deployment and deletes older ones that
have zero replicas.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: prune_stale_replicasets.py <replicasets-json>", file=sys.stderr)
        return 2

    json_path = Path(sys.argv[1])
    namespace = os.environ["OPENSHIFT_NAMESPACE"]
    kubeconfig_file = os.environ["KUBECONFIG_FILE"]

    with json_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for item in data.get("items", []):
        owner_refs = item.get("metadata", {}).get("ownerReferences", [])
        if not owner_refs:
            continue
        if any(ref.get("kind") != "Deployment" for ref in owner_refs):
            continue
        if item.get("status", {}).get("replicas", 0) not in (0, None):
            continue

        owner_name = owner_refs[0].get("name")
        if not owner_name:
            continue

        creation_ts = item.get("metadata", {}).get("creationTimestamp", "")
        name = item.get("metadata", {}).get("name")
        if not name:
            continue

        groups[owner_name].append((creation_ts, name))

    delete_names: list[str] = []
    for replicasets in groups.values():
        replicasets.sort(reverse=True)
        delete_names.extend(name for _, name in replicasets[2:])

    if not delete_names:
        print("No stale ReplicaSets found.")
        return 0

    print("Deleting stale ReplicaSets:")
    for name in delete_names:
        print(f" - {name}")
        subprocess.run(
            [
                "kubectl",
                "--kubeconfig",
                kubeconfig_file,
                "-n",
                namespace,
                "delete",
                "rs",
                name,
                "--wait=false",
            ],
            check=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
