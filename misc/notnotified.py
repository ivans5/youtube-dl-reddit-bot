#!env python3

import os,json,tempfile,re,subprocess,time

state_dir='/state/'

#1. check for new state files:
work_to_do=[]

items=[json.loads(open(os.path.join(state_dir, filename)).read())
    for filename in filter(lambda x: x.endswith(".json"), os.listdir(state_dir))]

items_notnotified_sorted = sorted(filter(lambda x: 'ipfs_hash' in x and not x['notifications'], items),
    key=lambda x: x['created'])

for item in items_notnotified_sorted:
  print (str(int(item['created']))+' '+item['youtube_id'])
  try:
    print ('  '+str(item['references']))
    print ('')
  except: continue

