import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

BRIDGE = Path(__file__).parent / 'node_bridge.cjs'
NODE = 'node'


def _run_node(action: str, params: Dict[str, Any]) -> Any:
    payload = json.dumps({'action': action, 'params': params})
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


def calculate(gen: int, attacker: Dict[str, Any], defender: Dict[str, Any], move: Dict[str, Any], field: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
