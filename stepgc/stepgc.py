#!env python3

import os,json,tempfile,re,subprocess,time
import sys

state_dir='/state/'

batch_size = 3
threshhold = 90  #percent%

if os.path.isfile('/state/gc_locked'):
    print ('GC_Locked, exiting...')
    quit()

items=[json.loads(open(os.path.join(state_dir, filename)).read()) 
    for filename in filter(lambda x: x.endswith(".json"), os.listdir(state_dir))]

#clear files who have exceed max attempts:
for item in filter(lambda x: x.get('step2_failed_attempts',0) > 5, items):
    print ('item exceed max attempts: '+(str(item)))
    os.system("mv -v -- /state/%s.json /state/old" % (item['youtube_id']))

#unpin X oldest videos:
items_sorted = sorted(filter(lambda x: 'ipfs_hash' in x, items),
    key=lambda x: x['created'])

def get_disk_used_percent():
    x=os.statvfs('/root/.ipfs')
    return 100*((x.f_blocks - x.f_bfree)/x.f_blocks)

#oldest items are first in the list:
while get_disk_used_percent() > threshhold:
    print ('disk used percent is: %f%%, threshhold is %f%%' % (get_disk_used_percent(), threshhold))
    for item in items_sorted[:batch_size]:
      if item['ipfs_hash'] != '-1': 
        print (item['youtube_id']+': '+str(item['created'])+' '+item['ipfs_hash'])
        print ('cleaning up item: '+(str(item)))
        retval=os.system("/root/goproject/bin/ipfs pin rm "+item['ipfs_hash'])
        if retval != 0:
          print ('Aborting! couldnt unpin item! Locking GC')
          open('/state/gc_locked','w')
          quit()
        os.system("mv -v -- /state/%s.json /state/old" % (item['youtube_id']))
    print ('Starting repo gc...')
    retval=os.system("/usr/bin/time /root/goproject/bin/ipfs repo gc")
    if retval != 0:
      print ('Aborting! couldnt run repo gc! Locking GC For now...')
      open('/state/gc_locked','w')
      quit()
    items_sorted = items_sorted[batch_size:]


#sleep for 20 mins:
print ('disk used percent is: %f%%, threshhold is %f%%' % (get_disk_used_percent(), threshhold))
print ('\033[1mSleeping for 20 minutes...\033[0m')
time.sleep(20 * 60)



    

