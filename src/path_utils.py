from pathlib import Path
import os


def get_project_root(start_path=None):
    """Return the workspace root by walking up from the provided path."""
    current = Path(start_path).resolve() if start_path else Path(__file__).resolve()
    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if (candidate / "app.py").exists() and (candidate / "Dataset").exists():
            return candidate

    return current


def resolve_project_path(*parts):
    """Resolve a path relative to the project root."""
    return str(get_project_root() / Path(*parts))


def resolve_dataset_path(filename="Afficionado_Coffee_Processed.csv", relative_folder="Dataset/Processed dataset"):
    """Resolve the processed dataset path from environment or workspace-relative locations."""
    env_path = os.getenv("AFFICIONADO_DATA_PATH")
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.exists():
            return str(candidate)

    project_root = get_project_root()
    candidates = [
        project_root / relative_folder / filename,
        project_root / "Dataset" / "Processed dataset" / filename,
        Path.cwd() / relative_folder / filename,
        Path.cwd() / filename,
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return str(project_root / relative_folder / filename)


def resolve_raw_data_path(filename="Afficionado Coffee Roasters.xlsx - Transactions.csv", relative_folder="Dataset/Raw dataset"):
    """Resolve the raw transactions CSV path from environment or workspace-relative locations."""
    env_path = os.getenv("AFFICIONADO_RAW_DATA_PATH")
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.exists():
            return str(candidate)

    project_root = get_project_root()
    candidates = [
        project_root / relative_folder / filename,
        project_root / "Dataset" / "Raw dataset" / filename,
        Path.cwd() / relative_folder / filename,
        Path.cwd() / filename,
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return str(project_root / relative_folder / filename)
