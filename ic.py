import sys
import os
import re
import time
try:
    from icecream import ic
    def outputFunction(*a):
        a=a[0]
        s=re.split(r'\:\d+ in ',a)
        file=s[0]
        a=a[len(file)+1:]
        s=re.split(r' in ',a)
        line=s[0]
        a=a[len(s[0])+4:]
        if '\n' in a:
            a=a.split('\n',1)
            a='- \n'.join(a)
        s=re.split(r'- ',a)
        func=s[0]
        a=a[len(func)+2:]
        args=a
        t=time.time()
        t='%.3f'%(t-int(t))
        at=time.asctime().split()
        at[3]+=t[1:]
        at=' '.join(at)
        print("\x1b[92mpid \x1b[94m"+str(os.getpid())+"\x1b[92m time \x1b[94m"+at+"\x1b[92m line \x1b[94m"+line+"\x1b[92m file \x1b[94m"+file+"\x1b[92m:\x1b[94m"+line+"\x1b[92m func \x1b[94m"+func+"\x1b[92m \x1b[0m"+args,file=sys.stderr)
    ic.configureOutput(includeContext=1)
    ic.configureOutput(outputFunction=outputFunction)
    ic.configureOutput(prefix='')
except Exception:
    ic=lambda *a:a[0] if len(a)==1 else [None,a][bool(a)]
