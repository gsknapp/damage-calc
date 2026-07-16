from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Pokemon:
    name: str
    gen: Optional[int] = None
    level: Optional[int] = None
    ability: Optional[str] = None
    abilityOn: Optional[bool] = None
    isDynamaxed: Optional[bool] = None
    dynamaxLevel: Optional[int] = None
    alliesFainted: Optional[int] = None
    boostedStat: Optional[str] = None
    item: Optional[str] = None
    gender: Optional[str] = None
    nature: Optional[str] = None
    ivs: Dict[str, int] = field(default_factory=dict)
    evs: Dict[str, int] = field(default_factory=dict)
    boosts: Dict[str, int] = field(default_factory=dict)
    originalCurHP: Optional[int] = None
    status: Optional[str] = None
    teraType: Optional[str] = None
    toxicCounter: Optional[int] = None
    moves: List[str] = field(default_factory=list)
    overrides: Dict[str, Any] = field(default_factory=dict)
    curHP: Optional[int] = None
