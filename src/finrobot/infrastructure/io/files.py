import os
import json
import pandas as pd
from typing import Annotated

SavePathType = Annotated[str, "File path to save data. If None, data is not saved."]


def save_output(data: pd.DataFrame, tag: str, save_path: SavePathType = None) -> None:
    if save_path:
        data.to_csv(save_path)
        print(f"{tag} saved to {save_path}")


def register_keys_from_json(file_path):
    with open(file_path, "r") as f:
        keys = json.load(f)
    for key, value in keys.items():
        os.environ[key] = value
