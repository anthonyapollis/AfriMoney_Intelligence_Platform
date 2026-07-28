"""Content-based "similar corridors" recommender for AfriMoney.

There's no local per-customer transaction data in this repo (the 40M+ row
synthetic dataset lived in Snowflake and was generated/torn down there,
per the project's zero-cost-by-design approach - only derived artifacts
like this map's corridor rollup survive locally). So, same reasoning as
the SA Property Intelligence "similar listings" stop in this rollout:
collaborative filtering needs interaction history this repo doesn't have
locally, but the 17-corridor rollup already embedded in
ebook/AfriMoney_Map.html (volume, success rate, FX spread, fraud bps,
average send, Mukuru/Mama Money split) is real, complete data - a
legitimate, honest basis for nearest-neighbour corridor similarity.

Useful framing: if corridor X is showing elevated fraud/risk, which
corridors have a similar profile and are worth a second look too.
"""
import json
import re
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parent.parent
MAP_HTML = BASE / "ebook" / "AfriMoney_Map.html"
OUT = BASE / "ml_models" / "corridor_similarity.json"

FEATURES = ["volume_m", "success_rate", "fx_spread", "fraud_bps", "avg_send", "mkr_pct"]


def parse_corridors():
    html = MAP_HTML.read_text(encoding="utf-8")
    m = re.search(r"const corridors = \[(.*?)\n\];", html, re.DOTALL)
    body = re.sub(r"//[^\n]*", "", m.group(1))
    objs = re.findall(r"\{([^{}]*)\}", body)
    corridors = []
    for o in objs:
        d = {}
        for key, val in re.findall(r'(\w+)\s*:\s*("[^"]*"|\[[^\]]*\]|[-\d.]+)', o):
            if val.startswith('"'):
                d[key] = val.strip('"')
            elif val.startswith("["):
                d[key] = re.findall(r'"([^"]*)"', val)
            else:
                d[key] = float(val) if "." in val else int(val)
        corridors.append(d)
    return corridors


def main():
    corridors = parse_corridors()
    print(f"parsed {len(corridors)} corridors from {MAP_HTML.name}")

    X = np.array([[c[f] for f in FEATURES] for c in corridors], dtype=float)
    X = StandardScaler().fit_transform(X)
    sim = cosine_similarity(X)
    np.fill_diagonal(sim, -1)

    results = []
    for i, c in enumerate(corridors):
        top = np.argsort(-sim[i])[:3]
        results.append({
            "id": c["id"],
            "name": c["name"],
            "city": c["city"],
            "volume_m": c["volume_m"],
            "fraud_bps": c["fraud_bps"],
            "success_rate": c["success_rate"],
            "similar": [
                {"id": corridors[j]["id"], "name": corridors[j]["name"],
                 "similarity": round(float(sim[i, j]), 3),
                 "fraud_bps": corridors[j]["fraud_bps"], "volume_m": corridors[j]["volume_m"]}
                for j in top
            ],
        })

    # diagnostic: does the nearest neighbour share the same volume cluster label?
    same_cluster = sum(
        1 for i, c in enumerate(corridors)
        if corridors[int(np.argsort(-sim[i])[0])]["cluster"] == c["cluster"]
    )
    metrics = {
        "model": "Content-based nearest-neighbour similarity (cosine) over real corridor KPIs",
        "corridors": len(corridors),
        "features": FEATURES,
        "diagnostic_nearest_neighbour_same_cluster_pct": round(100 * same_cluster / len(corridors), 1),
        "note": "17 corridors is too few for a held-out accuracy claim - this is a similarity tool for "
                "risk/ops triage (\"which corridors look like this one\"), not a validated prediction.",
    }
    print(json.dumps(metrics, indent=2))

    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"metrics": metrics, "corridors": results}, f, indent=2)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
