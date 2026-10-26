// SPD – echter Hook für 0.88 – braucht Shattered Pixel Dungeon Build
// Hookt: MeleeWeapon.damageRoll() -> Barrier.Buff.absorb() -> NormalIntRange(DRMin,DRMax)
// Erst wenn dieser Hook live Barrier+DR beobachtet, darf Torwart 0.88 geben
console.log("[A3-SPD] SPD Barrier vs DR Hook – TODO: attach to org.shatteredpixeldungeon");
Java.perform(function(){
  try{
    var MeleeWeapon = Java.use("com.shatteredpixel.shatteredpixeldungeon.items.weapon.melee.MeleeWeapon");
    MeleeWeapon.damageRoll.implementation = function(){
      var raw = this.damageRoll();
      console.log("[A3-SPD] damageRoll raw", raw);
      var res = this.damageRoll();
      send({type:"observed", finding_id:"spd_barrier_dr_order", provider:"a3_frida", target:"spd", observed:{damage_roll:raw, barrier_absorb_value:0, dr_min:0, dr_max:0, frida_version:Frida.version, device_id:"local", binary_sha256:"spd_build_hash", ts:Date.now()/1000}});
      return res;
    };
  }catch(e){ console.log("[A3-SPD] not in SPD process:", e); }
});
