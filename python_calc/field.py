from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class Side:
    spikes: int = 0
    steelsurge: bool = False
    vinelash: bool = False
    wildfire: bool = False
    cannonade: bool = False
    volcalith: bool = False
    isSR: bool = False
    isReflect: bool = False
    isLightScreen: bool = False
    isProtected: bool = False
    isSeeded: bool = False
    isSaltCured: bool = False
    isForesight: bool = False
    isTailwind: bool = False
    isHelpingHand: bool = False
    isFlowerGift: bool = False
    isPowerTrick: bool = False
    isFriendGuard: bool = False
    isAuroraVeil: bool = False
    isBattery: bool = False
    isPowerSpot: bool = False
    isSteelySpirit: bool = False
    isSwitching: Optional[Union[str, None]] = None


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

    def __post_init__(self) -> None:
        if self.attackerSide is None:
            self.attackerSide = Side()
        elif not isinstance(self.attackerSide, Side):
            self.attackerSide = Side(**self.attackerSide)

        if self.defenderSide is None:
            self.defenderSide = Side()
        elif not isinstance(self.defenderSide, Side):
            self.defenderSide = Side(**self.defenderSide)
