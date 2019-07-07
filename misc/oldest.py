#!env python3

import os,json,tempfile,re,subprocess,time
import sys

state_dir='/state/'


items=[json.loads(open(os.path.join(state_dir, filename)).read()) 
    for filename in filter(lambda x: x.endswith(".json"), os.listdir(state_dir))]

#clear files who have exceed max attempts:
for item in filter(lambda x: x.get('step2_failed_attempts',0) > 5, items):
    print ('item exceed max attempts: '+(str(item)))
    os.system("mv -v -- /state/%s.json /state/old" % (item['youtube_id']))

#unpin X oldest videos:
items_sorted = sorted(filter(lambda x: 'ipfs_hash' in x, items),
    key=lambda x: x['created'])

#oldest items are first in the list:
for item in items_sorted[:int(sys.argv[1])]:
        print (item['youtube_id']+': '+str(item['created'])+' '+item['ipfs_hash']+' '+str(item['filesize']))
    #check disk utilization
    #if space_used > XY%:
        print ('cleaning up item: '+(str(item)))
        os.system("/root/goproject/bin/ipfs pin rm "+item['ipfs_hash'])
        os.system("mv -v -- /state/%s.json /state/old" % (item['youtube_id']))
        #ipfs repo gc
    #else:
        #quit()
    #sleep




    

