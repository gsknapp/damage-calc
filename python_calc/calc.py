import json
import subprocess
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union
import copy

from pokemon import Pokemon

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


def calc_stat(gen: int, stat: str, base: int, iv: int, ev: int, level: int, nature: Optional[str] = None,isTransformedDitto : Optional[bool] = False) -> int:
    params = {
        'gen': gen,
        'stat': stat,
        'base': base,
        'iv': iv,
        'ev': ev,
        'level': level,
        'nature': nature,
        'isTransformedDitto':isTransformedDitto
    }
    return _run_node('calcStat', params)


def ditto_transform(m1 : Pokemon, m2 : Pokemon) -> tuple[Pokemon,Pokemon]:
    if m1.name == "Ditto":
        m1_transform = copy.deepcopy(m2)
        m1_transform.level = m1.level
        # not sure what to do about dynamax
        m1_transform.alliesFainted = m1.alliesFainted
        m1_transform.item = m1.item
        if m1.gen != None and 0 < m1.gen and m1.gen < 5:
            m1_transform.gender = m1.gender
        m1_transform.originalCurHP = m1.originalCurHP
        m1_transform.status = m1.status
        m1_transform.teraType = m1.teraType
        m1_transform.toxicCounter = m1.toxicCounter
        m1_transform.curHP = m1.curHP
        m1_transform.isTransformedDitto = True
        return m1_transform,m2
    elif m2.name == "Ditto":
        m2_transform = copy.deepcopy(m1)
        m2_transform.level = m2.level
        # not sure what to do about dynamax
        m2_transform.alliesFainted = m2.alliesFainted
        m2_transform.item = m2.item
        if m2.gen != None and 0 < m2.gen and m2.gen < 5:
            m2_transform.gender = m2.gender
        m2_transform.originalCurHP = m2.originalCurHP
        m2_transform.status = m2.status
        m2_transform.teraType = m2.teraType
        m2_transform.toxicCounter = m2.toxicCounter
        m2_transform.curHP = m2.curHP
        m2_transform.isTransformedDitto = True
        return m1,m2_transform
    else:
        return m1,m2