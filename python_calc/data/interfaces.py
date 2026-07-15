from typing import Dict, Iterable, Iterator, Optional, TypedDict, Any

StatID = str
StatsTable = Dict[StatID, int]

AbilityName = str
ItemName = str
MoveName = str
SpeciesName = str
TypeName = str
NatureName = str
StatusName = str
GameType = str
Terrain = str
Weather = str
MoveCategory = str
MoveTarget = str

class Ability(TypedDict, total=False):
    id: str
    name: AbilityName
    kind: str

class Item(TypedDict, total=False):
    id: str
    name: ItemName
    kind: str
    megaStone: Optional[Dict[SpeciesName, SpeciesName]]
    isBerry: bool
    naturalGift: Optional[Dict[str, Any]]

class MoveData(TypedDict, total=False):
    id: str
    name: MoveName
    kind: str
    basePower: int
    type: TypeName
    category: MoveCategory
    flags: Dict[str, Any]
    secondaries: Any
    target: MoveTarget
    recoil: Any
    hasCrashDamage: bool
    mindBlownRecoil: bool
    struggleRecoil: bool
    willCrit: bool
    drain: Any
    priority: int
    self: Any
    ignoreDefensive: bool
    overrideOffensiveStat: str
    overrideDefensiveStat: str
    overrideOffensivePokemon: str
    overrideDefensivePokemon: str
    breaksProtect: bool
    isZ: bool
    zMove: Any
    isMax: bool
    maxMove: Any
    multihit: Any
    multiaccuracy: bool

class Specie(TypedDict, total=False):
    id: str
    name: SpeciesName
    kind: str
    types: Any
    baseStats: StatsTable
    weightkg: float
    gender: str
    nfe: bool
    abilities: Dict[str, AbilityName]
    canGigantamax: MoveName
    otherFormes: list[SpeciesName]
    baseSpecies: SpeciesName

class TypeEffectiveness(TypedDict, total=False):
    pass

class TypeData(TypedDict, total=False):
    id: str
    name: TypeName
    kind: str
    effectiveness: Dict[TypeName, float]

class Nature(TypedDict, total=False):
    id: str
    name: NatureName
    kind: str
    plus: StatID
    minus: StatID
