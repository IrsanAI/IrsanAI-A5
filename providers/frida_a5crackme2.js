console.log("[A3] hook loading...");
const targetKey = "A5-Pro-Cockpit-2026!";

function tryHook(name){
  let addr=null;
  try{ addr=Module.findExportByName(null,name); }catch(e){}
  if(!addr) return false;
  console.log("[A3] hooking",name,addr);
  Interceptor.attach(addr,{
    onEnter(args){
      try{
        let s0 = args[0].readUtf8String();
        let s1 = args[1].readUtf8String();
        if(s0 && s1 && (s0.includes("A5-") || s1.includes("A5-") || s0.length>10)){
          console.log("[A3] "+name+" observed:",s0,"|",s1);
          send({type:"observed", func:name, a0:s0, a1:s1, ts:Date.now()});
        }
      }catch(e){}
    }
  });
  return true;
}
tryHook("strcmp");
tryHook("__strcmp");
tryHook("strncmp");
tryHook("memcmp");
