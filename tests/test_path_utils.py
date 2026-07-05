import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.path_utils import resolve_dataset_path


def test_resolve_dataset_path_points_to_existing_file():
    dataset_path = resolve_dataset_path()
    assert os.path.exists(dataset_path)
    assert dataset_path.endswith("Afficionado_Coffee_Processed.csv")
