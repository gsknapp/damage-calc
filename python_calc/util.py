import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / 'data'


def load_json(name: str) -> Any:
    path = DATA_DIR / f'{name}.json'
    with path.open(encoding='utf-8') as handle:
        data = json.load(handle)
    if isinstance(data, list) and len(data) == 1:
        return data[0]
    return data
