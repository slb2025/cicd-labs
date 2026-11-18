"""Prédiction des zones à risque à partir de l'historique Git (apprentissage SUPERVISÉ)."""

from __future__ import annotations

import argparse
import csv
import json
import pickle  # noqa: S403 — modèle produit localement
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score

MODEL = Path("reports/risk_model.pkl")
COVERAGE_MAP_PATH = Path("reports/coverage_test_map.json")
CORE_MODULES = {"minishop/pricing.py", "minishop/stock.py", "minishop/api.py"}

FEATURES = [
    "lines_added",
    "lines_deleted",
    "churn",
    "files_in_commit",
    "is_fix_commit",
    "late_hour",
    "file_past_commits",
    "file_past_breaks_rate",
    "author_past_breaks_rate",
    "is_code",
    "is_core",
]

TEST_MAP = {
    "minishop/pricing.py": ["tests/unit/test_pricing.py", "tests/generated"],
    "minishop/catalog.py": ["tests/unit", "tests/api"],
    "minishop/api.py": ["tests/api", "tests/e2e"],
    "minishop/static/": ["tests/e2e", "tests/visual"],
}


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def extract_row_features(
    f: str,
    la: int,
    ld: int,
    files_in_commit: int,
    is_fix_commit: int,
    hour: int,
    fc: int,
    fb: int,
    ac: int,
    ab: int,
) -> list[float]:
    return [
        float(la),
        float(ld),
        float(la + ld),
        float(files_in_commit),
        float(is_fix_commit),
        float(int(hour >= 20)),
        float(fc),
        fb / fc if fc else 0.0,
        ab / ac if ac else 0.0,
        float(int(f.endswith((".py", ".html", ".js")))),
        float(int(f in CORE_MODULES)),
    ]


def featurize(rows: list[dict]) -> tuple[np.ndarray, np.ndarray, dict]:
    """Variables calculées UNIQUEMENT avec le passé de chaque ligne (pas de fuite de données)."""
    file_commits, file_breaks = defaultdict(int), defaultdict(int)
    author_commits, author_breaks = defaultdict(int), defaultdict(int)
    X, y = [], []
    for r in rows:
        f, a = r["file"], r["author"]
        X.append(
            extract_row_features(
                f=f,
                la=int(r["lines_added"]),
                ld=int(r["lines_deleted"]),
                files_in_commit=int(r["files_in_commit"]),
                is_fix_commit=int(r["is_fix_commit"]),
                hour=int(r["hour"]),
                fc=file_commits[f],
                fb=file_breaks[f],
                ac=author_commits[a],
                ab=author_breaks[a],
            )
        )
        y.append(int(r["broke_ci"]))
        file_commits[f] += 1
        file_breaks[f] += int(r["broke_ci"])
        author_commits[a] += 1
        author_breaks[a] += int(r["broke_ci"])
    state = {
        "file_commits": dict(file_commits),
        "file_breaks": dict(file_breaks),
        "author_commits": dict(author_commits),
        "author_breaks": dict(author_breaks),
    }
    return np.array(X, dtype=float), np.array(y), state


def train(csv_path: Path) -> int:
    rows = load(csv_path)
    X, y, state = featurize(rows)
    cut = int(len(X) * 0.75)
    models = {
        "Régression logistique (balanced + churn/is_core)": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Gradient boosting": GradientBoostingClassifier(random_state=0),
    }
    best, best_auc = None, -1.0
    print(f"{len(X)} lignes — apprentissage sur {cut}, test sur {len(X) - cut} (les plus récentes)\n")
    for name, m in models.items():
        m.fit(X[:cut], y[:cut])
        proba = m.predict_proba(X[cut:])[:, 1]
        auc = roc_auc_score(y[cut:], proba)
        print(f"== {name} : AUC = {auc:.3f}")
        print(classification_report(y[cut:], (proba >= 0.5).astype(int), target_names=["ok", "casse"], zero_division=0))
        if auc > best_auc:
            best, best_auc = m, auc
    best.fit(X, y)
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    MODEL.write_bytes(pickle.dumps({"model": best, "state": state}))
    print(f"Modèle sauvegardé : {MODEL}")
    return 0


def changed_files(ref: str) -> list[tuple[str, int, int]]:
    out = subprocess.run(["git", "diff", "--numstat", ref], capture_output=True, text=True, check=True).stdout
    res = []
    for line in out.splitlines():
        a, d, f = line.split("\t")
        res.append((f, int(a) if a.isdigit() else 0, int(d) if d.isdigit() else 0))
    return res


def load_test_mapping() -> dict[str, list[str]]:
    if COVERAGE_MAP_PATH.exists():
        dynamic_map = json.loads(COVERAGE_MAP_PATH.read_text(encoding="utf-8"))
        merged = dict(TEST_MAP)
        merged.update(dynamic_map)
        return merged
    return TEST_MAP


def predict(files: list[tuple[str, int, int]], author: str, hour: int) -> int:
    bundle = pickle.loads(MODEL.read_bytes())  # noqa: S301
    m, st = bundle["model"], bundle["state"]
    scored = []
    for f, a, d in files:
        fc, fb = st["file_commits"].get(f, 0), st["file_breaks"].get(f, 0)
        ac, ab = st["author_commits"].get(author, 0), st["author_breaks"].get(author, 0)
        x = [extract_row_features(f, a, d, len(files), 0, hour, fc, fb, ac, ab)]
        scored.append((f, float(m.predict_proba(np.array(x, dtype=float))[0, 1])))
    scored.sort(key=lambda t: -t[1])

    test_mapping = load_test_mapping()
    order: list[str] = []
    for f, _ in scored:
        if f in test_mapping:
            order += [t for t in test_mapping[f] if t not in order]
        else:
            for prefix, tests in test_mapping.items():
                if f.startswith(prefix):
                    order += [t for t in tests if t not in order]

    print("Risque estimé par fichier modifié :")
    for f, p in scored:
        print(f"  {p:6.1%}  {f}")
    print("\nOrdre de test proposé :", " ".join(order) or "(aucun test ciblé : suite complète)")
    Path("reports").mkdir(exist_ok=True)
    Path("reports/tests_to_run.txt").write_text(" ".join(order) + "\n", encoding="utf-8")
    Path("reports/risk.json").write_text(json.dumps(dict(scored), indent=2), encoding="utf-8")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train")
    t.add_argument("csv", type=Path)
    p = sub.add_parser("predict")
    p.add_argument("--files", nargs="*", default=[])
    p.add_argument("--git-diff", help="référence git à comparer (ex. origin/main)")
    p.add_argument("--author", default="alice")
    p.add_argument("--hour", type=int, default=15)
    args = ap.parse_args()
    if args.cmd == "train":
        return train(args.csv)
    files = changed_files(args.git_diff) if args.git_diff else [(f, 30, 10) for f in args.files]
    return predict(files, args.author, args.hour)


if __name__ == "__main__":
    sys.exit(main())
