const path = require('path');
const fs = require('fs');
const calc = require(path.join(__dirname, '../calc/dist/index.js'));

function getGeneration(gen) {
  if (typeof gen === 'number') return calc.Generations.get(gen);
  if (typeof gen === 'string' && gen.match(/^\d+$/)) return calc.Generations.get(parseInt(gen, 10));
  return gen;
}

function normalizePokemon(data) {
  return new calc.Pokemon(getGeneration(data.gen), data.name, {
    level: data.level,
    ability: data.ability,
    abilityOn: data.abilityOn,
    isDynamaxed: data.isDynamaxed,
    dynamaxLevel: data.dynamaxLevel,
    alliesFainted: data.alliesFainted,
    boostedStat: data.boostedStat,
    item: data.item,
    gender: data.gender,
    nature: data.nature,
    ivs: data.ivs,
    evs: data.evs,
    boosts: data.boosts,
    originalCurHP: data.originalCurHP,
    status: data.status,
    teraType: data.teraType,
    toxicCounter: data.toxicCounter,
    moves: data.moves,
    overrides: data.overrides,
    curHP: data.curHP,
    isTransformedDitto: data.isTransformedDitto,
  });
}

function normalizeMove(data) {
  return new calc.Move(getGeneration(data.gen), data.name, {
    ability: data.ability,
    item: data.item,
    useZ: data.useZ,
    useMax: data.useMax,
    overrideMove: data.overrideMove,
    isCrit: data.isCrit,
    isStellarFirstUse: data.isStellarFirstUse,
    hits: data.hits,
    timesUsed: data.timesUsed,
    timesUsedWithMetronome: data.timesUsedWithMetronome,
    overrides: data.overrides,
  });
}

function normalizeField(data) {
  return new calc.Field({
    gameType: data.gameType,
    weather: data.weather,
    terrain: data.terrain,
    isMagicRoom: data.isMagicRoom,
    isWonderRoom: data.isWonderRoom,
    isGravity: data.isGravity,
    isAuraBreak: data.isAuraBreak,
    isFairyAura: data.isFairyAura,
    isDarkAura: data.isDarkAura,
    isBeadsOfRuin: data.isBeadsOfRuin,
    isSwordOfRuin: data.isSwordOfRuin,
    isTabletsOfRuin: data.isTabletsOfRuin,
    isVesselOfRuin: data.isVesselOfRuin,
    attackerSide: data.attackerSide,
    defenderSide: data.defenderSide,
  });
}

function resultToJson(result) {
  return {
    gen: result.gen.num,
    attacker: {
      name: result.attacker.name,
      ability: result.attacker.ability,
      item: result.attacker.item,
      level: result.attacker.level,
      nature: result.attacker.nature,
      types: result.attacker.types,
      stats: result.attacker.stats,
      rawStats: result.attacker.rawStats,
      boosts: result.attacker.boosts,
      originalCurHP: result.attacker.originalCurHP,
      isDynamaxed: result.attacker.isDynamaxed,
      teraType: result.attacker.teraType,
      status: result.attacker.status,
      toxicCounter: result.attacker.toxicCounter,
    },
    defender: {
      name: result.defender.name,
      ability: result.defender.ability,
      item: result.defender.item,
      level: result.defender.level,
      nature: result.defender.nature,
      types: result.defender.types,
      stats: result.defender.stats,
      rawStats: result.defender.rawStats,
      boosts: result.defender.boosts,
      originalCurHP: result.defender.originalCurHP,
      isDynamaxed: result.defender.isDynamaxed,
      teraType: result.defender.teraType,
      status: result.defender.status,
      toxicCounter: result.defender.toxicCounter,
    },
    move: {
      name: result.move.name,
      originalName: result.move.originalName,
      type: result.move.type,
      category: result.move.category,
      bp: result.move.bp,
      hits: result.move.hits,
      isCrit: result.move.isCrit,
      isStellarFirstUse: result.move.isStellarFirstUse,
    },
    field: {
      gameType: result.field.gameType,
      weather: result.field.weather,
      terrain: result.field.terrain,
      isMagicRoom: result.field.isMagicRoom,
      isWonderRoom: result.field.isWonderRoom,
      isGravity: result.field.isGravity,
      isAuraBreak: result.field.isAuraBreak,
      isFairyAura: result.field.isFairyAura,
      isDarkAura: result.field.isDarkAura,
      isBeadsOfRuin: result.field.isBeadsOfRuin,
      isSwordOfRuin: result.field.isSwordOfRuin,
      isTabletsOfRuin: result.field.isTabletsOfRuin,
      isVesselOfRuin: result.field.isVesselOfRuin,
      attackerSide: result.field.attackerSide,
      defenderSide: result.field.defenderSide,
    },
    damage: result.damage,
    rawDesc: result.rawDesc,
  };
}

function main() {
  let raw = '';
  process.stdin.on('data', chunk => raw += chunk);
  process.stdin.on('end', () => {
    const request = JSON.parse(raw);
    let response;
    try {
      const params = request.params || {};
      switch (request.action) {
        case 'calculate': {
          const attacker = normalizePokemon(params.attacker);
          const defender = normalizePokemon(params.defender);
          const move = normalizeMove(params.move);
          const field = params.field ? normalizeField(params.field) : new calc.Field();
          const result = calc.calculate(params.gen, attacker, defender, move, field);
          response = {result: resultToJson(result)};
          break;
        }
        case 'calcStat': {
          const stat = calc.calcStat(params.gen, params.stat, params.base, params.iv, params.ev, params.level, params.nature, params.isTransformedDitto);
          response = {result: stat};
          break;
        }
        default:
          throw new Error(`Unknown action: ${request.action}`);
      }
    } catch (err) {
      response = {error: err.message || String(err)};
    }
    process.stdout.write(JSON.stringify(response));
  });
}

main();
