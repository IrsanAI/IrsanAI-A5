
Java.perform(function(){
  var Barrier = Java.use("com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier");
  var Char = Java.use("com.shatteredpixel.shatteredpixeldungeon.actors.Char");
  var ShieldBuff = Java.use("com.shatteredpixel.shatteredpixeldungeon.actors.buffs.ShieldBuff");
  var UUID = Java.use("java.util.UUID");
  // crisis-proof token in target process only
  var sessionToken = UUID.randomUUID().toString();
  var drRollVal = 0;
  var damageRollVal = 0;
  var attackIdCounter = 0;
  var currentAttackId = 0;

  Char.attack.overload('com.shatteredpixel.shatteredpixeldungeon.actors.Char').implementation = function(target){
    currentAttackId = ++attackIdCounter;
    drRollVal = 0;
    damageRollVal = 0;
    return this.attack(target);
  };

  var orig_drRoll = Char.drRoll;
  Char.drRoll.overload().implementation = function(){
    var v = orig_drRoll.call(this);
    drRollVal = v;
    return v;
  };

  var orig_damageRoll = Char.damageRoll.overload().implementation;
  Char.damageRoll.overload().implementation = function(){
    var v = this.damageRoll();
    damageRollVal = v;
    return v;
  };

  ShieldBuff.absorbDamage.implementation = function(dmg){
    // Barrier-only
    if (this.getClass().getName().indexOf("Barrier")==-1){
      return this.absorbDamage(dmg);
    }
    var res = this.absorbDamage(dmg);
    // correlated evidence
    try{
      send({type:"spd_evidence", data:{
        _barrier_absorb: dmg - res,
        _dr_roll: drRollVal,
        _damage_roll: damageRollVal,
        _attack_id: currentAttackId,
        _order: "dr_before_barrier",
        _barrier_class: "com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier",
        frida_session_token: sessionToken,
        source: "frida_js",
        _source: "frida_js"
      }});
    }catch(e){}
    return res;
  };
});
