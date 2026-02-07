"""
label_grooming.py - PASYDA grooming labelling script

Labelling script PASYDA datasets.
Labels each conversation as:
- yes > grooming detected
- no > grooming not detected

Uses behvaioural metadata to generate labels.
"""

import pandas as pd
from pathlib import Path


YES = "yes"
NO = "no"
LABEL_COL = "grooming_label"


def label_victim_file(victim_csv: Path, solutions_csv: Path, out_dir: Path) -> Path:
    """
    Label one victim CSV using its matching solutions CSV.
    A row is labelled YES if its ID appears in the solutions file.
    """
    victim_df = pd.read_csv(victim_csv)
    sol_df = pd.read_csv(solutions_csv)

    if "ID" not in victim_df.columns:
        raise KeyError(f"{victim_csv.name} missing required column: ID")
    if "ID" not in sol_df.columns:
        raise KeyError(f"{solutions_csv.name} missing required column: ID")

    solution_ids = set(sol_df["ID"].astype(str))
    victim_ids = victim_df["ID"].astype(str)

    victim_df[LABEL_COL] = victim_ids.apply(
        lambda x: YES if x in solution_ids else NO
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{victim_csv.stem}_labelled.csv"
    victim_df.to_csv(out_path, index=False)

    return out_path


# ---------------------------
# Dataset pairing 
# ---------------------------
def find_pairs(dataset_dir: Path):
    """
    Find matching dataset pairs of the form:
    perp_X_vic_data.csv <-> perp_X_solutions.csv
    """
    victims = sorted(dataset_dir.glob("perp_*_vic_data.csv"))
    pairs = []

    for vic in victims:
        prefix = vic.name.replace("_vic_data.csv", "")
        sol = dataset_dir / f"{prefix}_solutions.csv"

        if sol.exists():
            pairs.append((vic, sol))
        else:
            print(f"[WARN] Missing solutions file for {vic.name}")

    return pairs


# ---------------------------
# Main with helper functions
# ---------------------------
def main():
    dataset_dir = Path("Dataset")
    out_dir = Path("outputs")

    if not dataset_dir.exists():
        raise FileNotFoundError(
            "Expected a 'Dataset' folder in the repository root."
        )

    pairs = find_pairs(dataset_dir)
    if not pairs:
        raise FileNotFoundError(
            "No perp_*_vic_data.csv files found in Dataset/"
        )

    labelled_frames = []

    for victim_csv, solutions_csv in pairs:
        out_path = label_victim_file(victim_csv, solutions_csv, out_dir)
        print(f"[OK] Labelled {victim_csv.name} -> {out_path}")
        labelled_frames.append(pd.read_csv(out_path))

    combined = pd.concat(labelled_frames, ignore_index=True)
    combined_out = out_dir / "all_victims_labelled.csv"
    combined.to_csv(combined_out, index=False)

    print(f"[OK] Combined labelled dataset saved to: {combined_out}")


if __name__ == "__main__":
    main()
