#!env python3
#
import os,json,tempfile,re,subprocess,time

state_dir='state/'

#1. check for new state files:
work_to_do=[]
for filename in os.listdir(state_dir):
   #TODO: verify json schema...
   if filename.endswith(".json"):
     item=json.loads(open(os.path.join(state_dir, filename)).read())
     if 'ipfs_hash' not in item:
       print ('Will try and download '+item['youtube_id'])
       work_to_do.append(item)

#2. download using youtube-dl, add to ipfs and get ipfs_hash:
for item in work_to_do:
    json_filename = "%s/%s.json" % (state_dir, item['youtube_id'])
    YouTubeURL = 'https://www.youtube.com/watch?v='+item['youtube_id']
    #2A. Try to download youtube video using youtube-dl:
    f = tempfile.TemporaryDirectory()
    print('%s/%s Starting download...' % (f.name,YouTubeURL))
    retval=os.system("cd "+f.name+" && youtube-dl --max-filesize 250.0m "+YouTubeURL) #TODO: stream output to client
    if retval != 0:
      print("Error running youtube-dl, Got retval: "+str(retval));
      item['step2_failed_attempts'] = item.get('step2_failed_attempts', 0) + 1
      open(json_filename,"w").write(json.dumps(item, indent=4, sort_keys=True))
      continue
    #2B. Pin to IPFS and get hash:
    try:
      filename=os.listdir(f.name)[0]
    except IndexError: #retval was 0 but filesize was too big...
      item['step2_failed_attempts'] = item.get('step2_failed_attempts', 0) + 1
      open(json_filename,"w").write(json.dumps(item, indent=4, sort_keys=True))
      continue 
    if not re.match('.*\.(?:mkv|mp4|webm)$', filename):
      print('Error - found non matching extension: '+filename)
      continue
    result=subprocess.run(['/root/goproject/bin/ipfs','add', '--quieter', f.name+'/'+filename],stdout=subprocess.PIPE)
    if result.returncode != 0:
      print ('Error couldnt Add to IPFS: '+YouTubeURL)
      continue
    ipfs_hash = result.stdout.decode("utf-8").rstrip()
    if not ipfs_hash.startswith('Qm'):
      print ('Error couldnt Add to IPFS: '+YouTubeURL)
      continue
    #2C. Update state file:
    item=json.loads(open(json_filename).read())
    item['ipfs_hash'] = ipfs_hash
    item['filesize'] = os.path.getsize(f.name+'/'+filename)
    open(json_filename,"w").write(json.dumps(item, indent=4, sort_keys=True))
    
    
#4. sleep 20mins...
print ('\033[1mSleeping for 20 minutes...\033[0m')
time.sleep(20 * 60)

