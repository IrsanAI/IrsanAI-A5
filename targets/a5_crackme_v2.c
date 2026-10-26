/* A5-CrackMe v2 – LEGAL TEST TARGET – MIT License – IrsanAI-A5 Pro
 * Key: A5-Pro-Cockpit-2026! (20 chars)
 * Build: gcc -O2 -o ~/a5_targets/a5_crackme_v2 targets/a5_crackme_v2.c
 */
#include <stdio.h>
#include <string.h>
#include <time.h>
#define KEY_LEN 20
char obf[] = {0x04,0x70,0x68,0x15,0x37,0x2a,0x68,0x06,0x2a,0x26,0x2e,0x35,0x2c,0x31,0x68,0x77,0x75,0x77,0x73,0x64};
int check(char *in){
  if((int)strlen(in)!=KEY_LEN) return 0;
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
