// SPDX-License-Identifier: Apache-2.0
// A3 FRIDA v3 – per-attack correlated, drRoll BEFORE damageRoll, Barrier-only, reset, send() to runner

Java.perform(function(){
  var Char = Java.use("com.shatteredpixel.shatteredpixeldungeon.actors.Char");
  var ShieldBuff = Java.use("com.shatteredpixel.shatteredpixeldungeon.actors.buffs.ShieldBuff");

  var currentAttack = null;
  var attackId = 0;

  // attack() ist Start – hier beginnt echter Angriffspfad
  function startAttack(attacker, defender){
    attackId++;
    currentAttack = {
      id: attackId,
      attacker: attacker ? attacker.toString().substring(0,80) : "unknown",
      defender: defender ? defender.toString().substring(0,80) : "unknown",
      drRoll: null,
      damageRoll: null,
      tsStart: Date.now()
    };
    console.log("[SPD] attack#" + attackId + " START attacker=" + currentAttack.attacker + " defender=" + currentAttack.defender);
  }

  // hook both overloads of attack
  var attack1 = Char.attack.overload('com.shatteredpixel.shatteredpixeldungeon.actors.Char');
  var attack2 = Char.attack.overload('com.shatteredpixel.shatteredpixeldungeon.actors.Char','float','float','float');
  
  Char.attack.overload('com.shatteredpixel.shatteredpixeldungeon.actors.Char').implementation = function(enemy){
    startAttack(this, enemy);
    return attack1.call(this, enemy);
  };
  Char.attack.overload('com.shatteredpixel.shatteredpixeldungeon.actors.Char','float','float','float').implementation = function(enemy, dmgMulti, dmgBonus, accMulti){
    startAttack(this, enemy);
    return attack2.call(this, enemy, dmgMulti, dmgBonus, accMulti);
  };

  // drRoll – kommt VOR damageRoll (Manus Fix) – 390 vor 415
  var drOverload = Char.drRoll.overload();
  Char.drRoll.overload().implementation = function(){
    var result = drOverload.call(this);
    if(currentAttack && (Date.now() - currentAttack.tsStart) < 2000){
      currentAttack.drRoll = result;
      console.log("[SPD] attack#" + currentAttack.id + " drRoll=" + result + " (BEFORE damageRoll)");
    }
    return result;
  };

  // damageRoll – stored overload, EINMAL
  var dmgOverload = Char.damageRoll.overload();
  Char.damageRoll.overload().implementation = function(){
    var result = dmgOverload.call(this);
    if(currentAttack && (Date.now() - currentAttack.tsStart) < 2000){
      currentAttack.damageRoll = result;
      console.log("[SPD] attack#" + currentAttack.id + " damageRoll=" + result + " (AFTER drRoll, correlated)");
    } else {
      // falls attack() nicht gehookt (edge), trotzdem neuen Kontext starten
      attackId++;
      currentAttack = {id: attackId, attacker: this.toString().substring(0,80), defender: "unknown", drRoll: null, damageRoll: result, tsStart: Date.now()};
    }
    return result;
  };

  // absorbDamage – nur Barrier, nur wenn gleicher Angriff, dr + dmg vorhanden, <2s, dann send() + Reset
  var absorbOverload = ShieldBuff.absorbDamage.overload('int');
  ShieldBuff.absorbDamage.overload('int').implementation = function(dmg){
    var before = this.shielding();
    var leftover = absorbOverload.call(this, dmg);
    var after = this.shielding();
    var absorbed = dmg - leftover;
    var buffType = this.getClass().getName();
    var isBarrier = buffType.indexOf("Barrier") !== -1;

    if(currentAttack && isBarrier && currentAttack.drRoll !== null && currentAttack.damageRoll !== null && (Date.now() - currentAttack.tsStart) < 2000){
      var ev = {
        attackId: currentAttack.id,
        attacker: currentAttack.attacker,
        defender: currentAttack.defender,
        ts: Date.now(),
        damageRoll: currentAttack.damageRoll,
        drRoll: currentAttack.drRoll,
        incomingDmg: dmg,
        absorbed: absorbed,
        leftover: leftover,
        shieldingBefore: before,
        shieldingAfter: after,
        buffType: buffType,
        correlated: true,
        order: "dr_before_barrier"
      };
      console.log("[SPD CORRELATED BARRIER] " + JSON.stringify(ev));
      
      // Wichtig: send() an Python Runner, nicht nur console.log (Manus Fix)
      try{
        send({type: "spd_evidence", data: ev});
      }catch(e){ console.log("[SPD] send failed: " + e); }

      // Reset – bindet an konkreten attack() Aufruf, verhindert Wiederverwendung (Manus Fix)
      currentAttack = null;
    }
    return leftover;
  };

  console.log("[SPD HOOK v3] Ready – attack() start, drRoll BEFORE damageRoll, Barrier-only, reset, send()");
});
