from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Result:
    gen: int
    attacker: Dict[str, Any]
    defender: Dict[str, Any]
    move: Dict[str, Any]
    field: Dict[str, Any]
    damage: List[int]
    rawDesc: Optional[str] = None
