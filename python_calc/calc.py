import json
import subprocess
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

BRIDGE = Path(__file__).parent / 'node_bridge.cjs'
NODE = 'node'


Jsonable = Union[Dict[str, Any], str, int, float, bool, None, list]


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_to_jsonable(v) for v in value]
    return value


def _run_node(action: str, params: Dict[str, Any]) -> Any:
    payload = json.dumps({'action': action, 'params': _to_jsonable(params)})
    proc = subprocess.run(
        [NODE, str(BRIDGE)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f'Node bridge failed: {proc.stderr.strip()}')
    response = json.loads(proc.stdout)
    if 'error' in response:
        raise RuntimeError(response['error'])
    return response['result']


def calculate(
    gen: int,
    attacker: Union[Dict[str, Any], Any],
    defender: Union[Dict[str, Any], Any],
    move: Union[Dict[str, Any], Any],
    field: Optional[Union[Dict[str, Any], Any]] = None,
) -> Dict[str, Any]:
    params = {
        'gen': gen,
        'attacker': attacker,
        'defender': defender,
        'move': move,
        'field': field or {},
    }
    return _run_node('calculate', params)


def calc_stat(gen: int, stat: str, base: int, iv: int, ev: int, level: int, nature: Optional[str] = None) -> int:
    params = {
        'gen': gen,
        'stat': stat,
        'base': base,
        'iv': iv,
        'ev': ev,
        'level': level,
        'nature': nature,
    }
    return _run_node('calcStat', params)
