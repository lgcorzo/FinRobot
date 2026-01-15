"""Infrastructure IO - File utilities."""

import json
import os
import typing as T

SavePathType = T.Union[str, os.PathLike, None]


def save_output(
    data: T.Any,
    name: str,
    save_path: SavePathType = None,
) -> None:
    """Save output data to a file.

    Parameters:
        data (Any): data to save.
        name (str): name of the data (for logging).
        save_path (SavePathType): path to save the data.
    """
    if save_path:
        if hasattr(data, "to_csv"):
            data.to_csv(save_path)
        elif isinstance(data, (dict, list)):
            with open(save_path, "w") as f:
                json.dump(data, f, indent=4)
        else:
            with open(save_path, "w") as f:
                f.write(str(data))
        print(f"{name} saved to {save_path}")


def register_keys_from_json(path: str) -> None:
    """Register API keys from a JSON file.

    Parameters:
        path (str): path to the JSON file.
    """
    if os.path.exists(path):
        if os.path.isdir(path):
            # If directory, look for config_api_keys or similar?
            # Original code likely handled this.
            # For now, let's assume it's a file or handle it if it exists as a file.
            pass
        else:
            with open(path, "r") as f:
                config = json.load(f)
            for k, v in config.items():
                os.environ[k] = str(v)
                # print(f"Registered {k} from {path}")
