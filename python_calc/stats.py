from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Stats:
    hp: Optional[int] = None
    atk: Optional[int] = None
    def_: Optional[int] = None
    spa: Optional[int] = None
    spd: Optional[int] = None
    spe: Optional[int] = None

    def to_dict(self) -> Dict[str, Optional[int]]:
        return {
            'hp': self.hp,
            'atk': self.atk,
            'def': self.def_,
            'spa': self.spa,
            'spd': self.spd,
            'spe': self.spe,
        }
