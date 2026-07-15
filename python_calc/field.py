from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Side(Enum):
    ATTACKER = 'attacker'
    DEFENDER = 'defender'


@dataclass
class Field:
    gameType: Optional[str] = None
    weather: Optional[str] = None
    terrain: Optional[str] = None
    isMagicRoom: Optional[bool] = None
    isWonderRoom: Optional[bool] = None
    isGravity: Optional[bool] = None
    isAuraBreak: Optional[bool] = None
    isFairyAura: Optional[bool] = None
    isDarkAura: Optional[bool] = None
    isBeadsOfRuin: Optional[bool] = None
    isSwordOfRuin: Optional[bool] = None
    isTabletsOfRuin: Optional[bool] = None
    isVesselOfRuin: Optional[bool] = None
    attackerSide: Optional[Side] = None
    defenderSide: Optional[Side] = None
