#include <stdio.h>
#include <string.h>
static int check_password(const char *s){ return strcmp(s,"kq4-test")==0; }
int main(int c,char**v){ if(c>1&&check_password(v[1])) puts("OK"); else puts("NO"); return 0; }
