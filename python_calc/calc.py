import json
import subprocess
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union
import copy
from math import ceil

from pokemon import Pokemon
from field import Field
from move import Move

BRIDGE = Path(__file__).parent / 'node_bridge.cjs'
NODE = 'node'


Jsonable = Union[Dict[str, Any], str, int, float, bool, None, list]

current_gen = 9


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
    attacker: Union[Dict[str, Any], Any],
    defender: Union[Dict[str, Any], Any],
    move: Union[Dict[str, Any], Any],
    gen: int = current_gen,
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


def calc_stat(stat: str, base: int, iv: int, ev: int, level: int, gen: int = current_gen,nature: Optional[str] = None,isTransformedDitto : Optional[bool] = False) -> int:
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
    
def best_damaging_move(attacker:Pokemon,defender:Pokemon, gen : int = current_gen, field :Field = Field()) -> str:
    """Returns the name of attacker's best damaging move against defender"""
    max_damage = 0
    max_damaging_move = ""
    for move_name in attacker.moves:
        move = Move(name=move_name,gen=gen)
        damages = calculate(gen=gen,attacker=attacker,defender=defender,move=move,field=field)["damage"]
        if isinstance(damages,list) and damages[-1] >= max_damage:
            max_damage = damages[-1]
            max_damaging_move=move_name
    return max_damaging_move
    

# consider accounting for recoil, priority, stat dropping moves (e.g. overheat), average instead of minimum damage?
# also consider making best_damaging_move return the relevant information so that calculate is really only ever run 8 times
# instead of 10
def one_v_one_calcs(
        m1 : Pokemon,
        m2 : Pokemon,
        gen : int = current_gen,
        field : Field = Field()) -> tuple[list,list]:
    """Returns a pair of lists l1, l2 where each list contains the information necessary to compute advantage.
    
    Specifically, li = [di, mi_cur_hp, mi_spe, mi_is_ditto] where di is the minimum amount of raw HP damage that mi does to mj with
    its best damaging move, mi_spe is mi's speed stat, and mi_is_ditto is a flag indicating whether mi is ditto.
    
    This is a relatively expensive computation, and it can only needs to be run once when computing any of the advantage
    variations, so we separate this computation into its own method.
    
    Field is assumed to be from m1's perspective so that field.attackerSide = m1_side."""

    # check for Dittos and transform
    m1_is_ditto = (m1.name == "Ditto")
    m2_is_ditto = (m2.name == "Ditto")
    m1,m2= ditto_transform(m1,m2)

    m1_field = field
    m2_field = copy.deepcopy(field)
    m2_field.attackerSide = copy.deepcopy(field.defenderSide)
    m2_field.defenderSide = copy.deepcopy(field.attackerSide)

    # identify best moves
    m1_best_damaging_move = best_damaging_move(gen=gen,attacker=m1,defender=m2,field=m1_field)
    m2_best_damaging_move = best_damaging_move(gen=gen,attacker=m2,defender=m1,field=m2_field)

    # get damage and stat calcs
    m1_to_m2_calc = calculate(gen=gen,attacker=m1,defender=m2,move=Move(gen=gen,name=m1_best_damaging_move),field=m1_field)
    m2_to_m1_calc = calculate(gen=gen,attacker=m2,defender=m1,move=Move(gen=gen,name=m2_best_damaging_move),field=m2_field)

    # get raw damage
    if isinstance(m1_to_m2_calc['damage'],list):
        m1_to_m2_damage = m1_to_m2_calc["damage"][0]
    else:
        m1_to_m2_damage = m1_to_m2_calc['damage']
    if isinstance(m2_to_m1_calc['damage'],list):
        m2_to_m1_damage = m2_to_m1_calc["damage"][0]
    else:
        m2_to_m1_damage = m2_to_m1_calc['damage']

    # get current hps
    m1_cur_hp = m1_to_m2_calc['attacker']['originalCurHP']
    m2_cur_hp = m2_to_m1_calc['attacker']['originalCurHP']

    # getting speeds from stats (rather than rawStats) automatically builds in scarf and tailwind boosts.
    m1_spe = m1_to_m2_calc['attacker']['stats']['spe']
    m2_spe = m2_to_m1_calc['attacker']['stats']['spe']

    return [m1_to_m2_damage, m1_cur_hp, m1_spe, m1_is_ditto], [m2_to_m1_damage, m2_cur_hp, m2_spe, m2_is_ditto]


def advantage(
        m1 : Pokemon,
        m2 : Pokemon,
        gen : int = current_gen,
        field : Field = Field(),
        m1_cur_hp : int = -1,
        m2_cur_hp : int = -1,
        num_hp_states : int = 1) -> float:
    """Returns the damage differential in a hypothetical one-on-one matchup between m1 and m2.

    Assumes that each Pokemon will repeatedly select its best damaging move until a KO is achieved.  Calculates total damage dealt
    in that one-on-one matchup as a fraction of opponent's current HP (max of 1, as overkill damage is meaningless). Returns the 
    differential in those fractions.
    
    Currently, num_hp_states does nothing."""

    assert num_hp_states >= 1, "Number of HP states must be a positive integer."

    l1,l2 = one_v_one_calcs(m1=m1,m2=m2,gen=gen,field=field)

    # get current HPs
    if m1_cur_hp == -1:
        m1_cur_hp = l1[1]
    if m2_cur_hp == -1:
        m2_cur_hp = l2[1]

    # get damage of best moves as fraction of opponent's current HP
    m1_to_m2_damage = l1[0] / m2_cur_hp
    m2_to_m1_damage = l2[0] / m1_cur_hp

    # get speeds
    m1_spe = l1[2]
    m2_spe = l2[2]

    # get Ditto status
    m1_is_ditto = l1[3]
    m2_is_ditto = l2[3]

    # if either mon has already been KOd
    if m1_cur_hp == 0 and m2_cur_hp == 0:
        return 0
    elif m1_cur_hp == 0:
        return -1
    elif m2_cur_hp == 0:
        return 1


    # figure out when the KO will occur
    try:
        m1_ttko_m2 = ceil(max(1, 1 / m1_to_m2_damage))
        m2_ttko_m1 = ceil(max(1, 1 / m2_to_m1_damage))
    except ZeroDivisionError:
        if m1_to_m2_damage == 0 and m2_to_m1_damage == 0:
            return 0
        elif m1_to_m2_damage == 0:
            return -1
        else:
            return 1
    turn_of_ko = min(m1_ttko_m2,m2_ttko_m1)

    # handle the fact that Ditto only has 5 PP per move (and it is often locked into one move because it often holds Scarf);
    # this is awkward, could be revisited
    if m1_is_ditto and m1.item in ["Choice Scarf", "Choice Specs", "Choice Band"] and turn_of_ko > 5:
        return min(1, 5 * m1_to_m2_damage) - min(1, turn_of_ko * m2_to_m1_damage)
    elif m2_is_ditto and m2.item in ["Choice Scarf", "Choice Specs", "Choice Band"] and turn_of_ko > 5:
        return min(1, turn_of_ko * m1_to_m2_damage) - min(1, 5 * m2_to_m1_damage)
    
    # this is now the 'normal' case (when there either is no Choice-locked Ditto or toko <= 5)
    elif m1_spe > m2_spe and turn_of_ko == m1_ttko_m2: # if m1 is faster and KOs m2, m1 gets one more turn than m2
        return min(1, turn_of_ko * m1_to_m2_damage) - min(1, (turn_of_ko-1) * m2_to_m1_damage)
    elif m1_spe < m2_spe and turn_of_ko == m2_ttko_m1: # if m2 is faster and KOs m1, m2 gets one more turn than m1
        return min(1, (turn_of_ko - 1) * m1_to_m2_damage) - min(1, turn_of_ko * m2_to_m1_damage)
    else: # if the slower mon KOs the faster one, they take the same number of turns.  This also covers the case of a speed tie (could be revised).
        return min(1, turn_of_ko * m1_to_m2_damage) - min(1, turn_of_ko * m2_to_m1_damage)
    