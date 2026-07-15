from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Move:
    name: str
    ability: Optional[str] = None
    item: Optional[str] = None
    useZ: Optional[bool] = None
    useMax: Optional[bool] = None
    overrideMove: Optional[str] = None
    isCrit: Optional[bool] = None
    isStellarFirstUse: Optional[bool] = None
    hits: Optional[int] = None
    timesUsed: Optional[int] = None
    timesUsedWithMetronome: Optional[int] = None
    overrides: Dict[str, Any] = field(default_factory=dict)
    gen: Optional[int] = None
