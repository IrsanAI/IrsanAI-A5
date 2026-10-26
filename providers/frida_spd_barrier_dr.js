// SPDX-License-Identifier: Apache-2.0
// A3 FRIDA – SPD Barrier vs DR – correlated per-attack, Barrier-only, fail-closed honest
// Manus Fix: lastDamageRoll/drRoll dürfen nicht global stehen bleiben, Reset nach Absorb, nur Barrier

Java.perform(function(){
  var Char = Java.use("com.shatteredpixel.shatteredpixeldungeon.actors.Char");
  var ShieldBuff = Java.use("com.shatteredpixel.shatteredpixeldungeon.actors.buffs.ShieldBuff");

  var currentAttack = null; // {id, damageRoll, drRoll, tsDamage, tsDr}
  var attackId = 0;

  var dmgOverload = Char.damageRoll.overload();
  Char.damageRoll.overload().implementation = function(){
    var result = dmgOverload.call(this);
    attackId++;
    currentAttack = {id: attackId, damageRoll: result, drRoll: null, tsDamage: Date.now(), tsDr: null, attacker: this.toString().substring(0,80)};
    console.log("[SPD] attack#" + attackId + " damageRoll=" + result);
    return result;
  };

  var drOverload = Char.drRoll.overload();
  Char.drRoll.overload().implementation = function(){
    var result = drOverload.call(this);
    if(currentAttack && (Date.now() - currentAttack.tsDamage) < 1000){
      currentAttack.drRoll = result;
      currentAttack.tsDr = Date.now();
      console.log("[SPD] attack#" + currentAttack.id + " drRoll=" + result + " correlated to dmg=" + currentAttack.damageRoll);
    }
    return result;
  };

  var absorbOverload = ShieldBuff.absorbDamage.overload('int');
  ShieldBuff.absorbDamage.overload('int').implementation = function(dmg){
    var before = this.shielding();
    var result = absorbOverload.call(this, dmg);
    var after = this.shielding();
    var absorbed = dmg - result;
    var buffType = this.getClass().getName();

    // Nur Barrier, nicht irgendein ShieldBuff
    var isBarrier = buffType.indexOf("Barrier") !== -1;
    
    // Korrelation nur wenn gleicher Angriff, <1s, drRoll vorhanden, Barrier
    if(currentAttack && isBarrier && currentAttack.drRoll !== null && (Date.now() - currentAttack.tsDamage) < 1000){
      var ev = {
        attackId: currentAttack.id,
        ts: Date.now(),
        damageRoll: currentAttack.damageRoll,
        drRoll: currentAttack.drRoll,
        incomingDmg: dmg,
        absorbed: absorbed,
        leftover: result,
        shieldingBefore: before,
        shieldingAfter: after,
        buffType: buffType,
        correlated: true,
        order: "dr_before_barrier"
      };
      console.log("[SPD CORRELATED BARRIER] " + JSON.stringify(ev));

      // Evidence für Torwart – erst jetzt darf 0.88 möglich sein, aber nur mit echtem SHA + device_id
      var evidence = {
        evidence_id: "spd_barrier_dr_order-live-" + Date.now() + "-atk" + currentAttack.id,
        provider: "a3_frida",
        target: "spd",
        finding_id: "spd_barrier_dr_order",
        confidence: "observed",
        correlated: true,
        observed: {
          barrier_absorb_value: absorbed,
          shielding_before: before,
          shielding_after: after,
          dr_roll: currentAttack.drRoll,
          dr_min: currentAttack.drRoll,
          dr_max: currentAttack.drRoll,
          damage_roll: currentAttack.damageRoll,
          incoming_damage: dmg,
          leftover_damage: result,
          order: "dr_before_barrier",
          barrier_class: buffType,
          attack_id: currentAttack.id
        },
        frida_version: Frida.version,
        binary_sha256: "needs-real-apk-sha256-from-actual-build",
        device_id: "needs-real-device-id",
        timestamp: Date.now(),
        ts: Date.now()/1000
      };
      console.log("[SPD EVIDENCE] " + JSON.stringify(evidence));

      // Reset – bindet Korrelation an konkreten Angriff, verhindert Wiederverwendung globaler Werte (Manus Fix)
      currentAttack = null;
    }
    return result;
  };

  console.log("[SPD HOOK v2.1] Ready – per-attack correlated, Barrier-only, reset after absorb");
});
