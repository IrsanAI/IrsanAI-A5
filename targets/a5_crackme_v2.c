/* A5-CrackMe v2 – LEGAL TEST TARGET – 【entity-MIT¦canonical_name=MIT】 License – IrsanAI-A5 Pro
  * Ziel: A3 Frida + A4 capa + Torwart AAP testen, ohne Fremd-APK
  * Key: A5-Pro-Cockpit-2026!
  * Build: gcc -O2 -o a5_crackme_v2 a5_crackme_v2.c
 */
#include <stdio.h>
#include <string.h>
#include <time.h>
#define KEY "A5-Pro-Cockpit-2026!"
#define KEY_LEN 20
// simple XOR obfuscation to avoid plain string in binary
char obf[] = {0x04,0x60,0x2a,0x10,0x1a,0x02,0x2c,0x5c,0x24,0x0e,0x15,0x0a,0x1d,0x4d,0x62,0x60,0x62,0x61,0x62,0x00};
int check(char *in){
  if(strlen(in)!=KEY_LEN) return 0;
  for(int i=0;i<KEY_LEN;i++){ if((in[i]^0x45)!=obf[i]) return 0; }
  return 1;
}
int main(int argc,char **argv){
  if(argc<2){ printf("A5-CrackMe v2 – Usage: %s <key>\nHint: 20 chars, starts with A5-Pro\n",argv[0]); return 1; }
  clock_t s=clock();
  int ok=check(argv[1]);
  clock_t e=clock();
  double ms=(double)(e-s)/CLOCKS_PER_SEC*1000;
  if(ms>50) printf("[anti-debug] slow path %.2fms – debugger?\n",ms);
  if(ok) printf("[+] A5-CrackMe v2 PASS – Key OK – Evidence: observed\n");
  else printf("[-] FAIL – Try again – Evidence: inferred\n");
  return ok?0:2;
}
