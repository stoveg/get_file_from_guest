import time
import threading
cur_time = time.strftime('%Y%m%d', time.localtime(time.time()))

fl=[]

def a(x):

   print x,'+1', '=',x+1
   fl.append(str(x) + '+1'+'=' + str(x+1))
   print fl,'\n'


for x in range(1,10):
    threading.Thread(target=a,args=(x,)).start()
