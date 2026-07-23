import copy
from math import ceil,floor
import numpy as np
from typing import Any

from pokemon import Pokemon
from move import Move
from field import Field
from calc import calculate

current_gen = 9

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
    
# consider setting up the calc so that the field has the relevant terrain or weather for such setters
def best_damaging_move(attacker:Pokemon,defender:Pokemon, gen : int = current_gen, field : Field = Field()) -> tuple[str,float]:
    """Returns the name of attacker's best damaging move against defender"""
    max_damage = 0
    max_damaging_move = ""
    for move_name in attacker.moves:
        move = Move(name=move_name,gen=gen)
        damages = calculate(gen=gen,attacker=attacker,defender=defender,move=move,field=field)["damage"]
        if isinstance(damages,list): # damages could be a list of ints (single hit moves) or a list of lists of ints (multihit moves)
            if isinstance(damages[0],int):
                avg_move_damage = (damages[0] + damages[-1])/2
                if avg_move_damage >= max_damage:
                    max_damage = avg_move_damage
                    max_damaging_move=move_name
            if isinstance(damages[0],list):
                avg_move_damage = sum(damages[i][0] + damages[i][-1] for i in range(len(damages)))/2
                if avg_move_damage >= max_damage:
                    max_damage = avg_move_damage
                    max_damaging_move = move_name
    return max_damaging_move,max_damage
    

# consider accounting for recoil, priority, stat dropping moves (e.g. overheat)?
# also consider making best_damaging_move return the relevant information so that calculate is really only ever run 8 times
# instead of 10.  Probably should just be merged with best_damaging_move
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
    m1_best_damaging_move,m1_to_m2_damage = best_damaging_move(gen=gen,attacker=m1,defender=m2,field=m1_field)
    m2_best_damaging_move,m2_to_m1_damage = best_damaging_move(gen=gen,attacker=m2,defender=m1,field=m2_field)

    # get damage and stat calcs
    m1_to_m2_calc = calculate(gen=gen,attacker=m1,defender=m2,move=Move(gen=gen,name=m1_best_damaging_move),field=m1_field)
    m2_to_m1_calc = calculate(gen=gen,attacker=m2,defender=m1,move=Move(gen=gen,name=m2_best_damaging_move),field=m2_field)

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
        num_hp_states : int = 1,
        print_matrix : bool = False) -> np.floating:
    """
    Returns the average damage differential in a hypothetical one-on-one matchup between m1 and m2.

    Assumes that each Pokemon will repeatedly select its best damaging move until a KO is achieved.  Calculates total damage dealt
    in that one-on-one matchup as a fraction of opponent's current HP (max of 1, as overkill damage is meaningless). Returns the 
    differential in those fractions.
    
    Averages over many HP states to allow for the stat to account for 'if I can get 5% more damage on my opponent's __, then my __ sweeps'.
    
    Does not account for abilities which activate at low HP like Torrent (because I do not want to rerun calculate for each hp state).
    """

    assert num_hp_states >= 1, "Number of HP states must be a positive integer."

    l1,l2 = one_v_one_calcs(m1=m1,m2=m2,gen=gen,field=field)

    # get current HPs
    if m1_cur_hp == -1:
        m1_cur_hp = l1[1]
    if m2_cur_hp == -1:
        m2_cur_hp = l2[1]

    assert num_hp_states <= m1_cur_hp and num_hp_states <= m2_cur_hp, "Number of HP states cannot be larger than current HP"

    # handle the case where either mon has already been KOd
    if m1_cur_hp == 0 and m2_cur_hp == 0:
        return np.float64(0)
    elif m1_cur_hp == 0:
        return np.float64(-1)
    elif m2_cur_hp == 0:
        return np.float64(1)
    
    # get raw damages
    m1_to_m2_raw_damage = l1[0]
    m2_to_m1_raw_damage = l2[0]

    # handle the case where either pokemon is doing 0 damage to the other
    if m1_to_m2_raw_damage == 0 and m2_to_m1_raw_damage == 0:
        return np.float64(0)
    elif m1_to_m2_raw_damage == 0:
        return np.float64(-1)
    elif m2_to_m1_raw_damage == 0:
        return np.float64(1)

    # get speeds
    m1_spe = l1[2]
    m2_spe = l2[2]

    # get Ditto status
    m1_is_ditto = l1[3]
    m2_is_ditto = l2[3]

    advantages = np.zeros(shape=(num_hp_states,num_hp_states))

    for state_1 in range(num_hp_states):
        m1_temp_hp = floor((num_hp_states - state_1) / num_hp_states * m1_cur_hp)
        for state_2 in range(num_hp_states):
            m2_temp_hp = floor((num_hp_states - state_2) / num_hp_states * m2_cur_hp)

            # get damage of best moves as fraction of opponent's current HP
            m1_to_m2_damage = m1_to_m2_raw_damage / m2_temp_hp
            m2_to_m1_damage = m2_to_m1_raw_damage / m1_temp_hp

            # figure out when the KO will occur
            m1_ttko_m2 = ceil(max(1, 1 / m1_to_m2_damage)) # recall that we've already handled the case where denominator = 0
            m2_ttko_m1 = ceil(max(1, 1 / m2_to_m1_damage))
            turn_of_ko = min(m1_ttko_m2,m2_ttko_m1)

            # handle the fact that Ditto only has 5 PP per move (and it is often locked into one move because it often holds Scarf);
            # this is awkward, could be revisited
            if m1_is_ditto and m1.item in ["Choice Scarf", "Choice Specs", "Choice Band"] and turn_of_ko > 5:
                advantages[state_1,state_2] = min(1, 5 * m1_to_m2_damage) - min(1, turn_of_ko * m2_to_m1_damage)
            elif m2_is_ditto and m2.item in ["Choice Scarf", "Choice Specs", "Choice Band"] and turn_of_ko > 5:
                advantages[state_1,state_2] = min(1, turn_of_ko * m1_to_m2_damage) - min(1, 5 * m2_to_m1_damage)
            
            # this is now the 'normal' case (when there either is no Choice-locked Ditto or toko <= 5)
            elif m1_spe > m2_spe and turn_of_ko == m1_ttko_m2: # if m1 is faster and KOs m2, m1 gets one more turn than m2
                advantages[state_1,state_2] = min(1, turn_of_ko * m1_to_m2_damage) - min(1, (turn_of_ko-1) * m2_to_m1_damage)
            elif m1_spe < m2_spe and turn_of_ko == m2_ttko_m1: # if m2 is faster and KOs m1, m2 gets one more turn than m1
                advantages[state_1,state_2] = min(1, (turn_of_ko - 1) * m1_to_m2_damage) - min(1, turn_of_ko * m2_to_m1_damage)
            else: # if the slower mon KOs the faster one, they take the same number of turns.  This also covers the case of a speed tie (could be revised).
                advantages[state_1,state_2] = min(1, turn_of_ko * m1_to_m2_damage) - min(1, turn_of_ko * m2_to_m1_damage)

    if print_matrix:
        print(advantages)
    return np.mean(advantages)