// A5-CrackMe v2 – korrekter Hook: check(char*) mit strlen + XOR 0x45
console.log("[A3] hook loading correct – looking for check()");
function hookCheck() {
  let checkAddr = null;
  try { checkAddr = Module.findExportByName(null, "check"); } catch(e){}
  if (!checkAddr) {
    // Symbole durchsuchen
    try {
      let mods = Process.enumerateModules();
      for (let m of mods) {
        let syms = Module.enumerateSymbols(m.name);
        for (let s of syms) {
          if (s.name==="check" && s.type==="function") { checkAddr = s.address; break; }
        }
        if (checkAddr) break;
      }
    } catch(e){}
  }
  if (!checkAddr) { console.log("[A3] check() not found – hooking strlen instead"); return hookStrlen(); }
  console.log("[A3] hooking check() at", checkAddr);
  Interceptor.attach(checkAddr, {
    onEnter(args){
      try {
        this.input = args[0].readCString();
        console.log("[A3] check() called with:", this.input);
      } catch(e){ this.input=""; }
    },
    onLeave(retval){
      let res = retval.toInt32();
      console.log("[A3] check() returned:", res, "for", this.input);
      send({type:"observed", finding_id:"a5_crackme_v2_key_check", provider:"a3_frida", target:"a5_crackme_v2", input:this.input, result:res, ts:Date.now()});
    }
  });
  return true;
}
function hookStrlen(){
  let addr=null;
  try{ addr=Module.findExportByName(null,"strlen"); }catch(e){}
  if(!addr) return false;
  console.log("[A3] fallback hooking strlen at",addr);
  Interceptor.attach(addr,{
    onEnter(args){ try{ let s=args[0].readCString(); if(s && s.startsWith("A5-")) { console.log("[A3] strlen observed:",s); send({type:"observed", finding_id:"a5_crackme_v2_key_check", provider:"a3_frida", target:"a5_crackme_v2", input:s, func:"strlen", ts:Date.now()}); } }catch(e){} }
  });
  return true;
}
hookCheck();
