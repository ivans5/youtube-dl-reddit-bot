#!env python3
#
import os,json,re,random,time
import praw

state_dir='state/'
delay=600

reddit = praw.Reddit(client_id='REDACTED',
                     client_secret='REDACTED',
                      user_agent='my user agent',
  username='YourUsername',
                     password='REDACTED')

print(reddit.read_only)  # Output: False

mymessages_old = [
'Greetings earthlings, We have detected that this video is blocked in CANADA, but fear not! A mirror was found, https://ipfs.io/ipfs/%s',
'Blocked in Canada :(, but my friend sent me a mirror that works at: https://ipfs.io/ipfs/%s',
'Hmm for me it says Blocked in Canada, but i looked around and found another link to the video at: https://ipfs.io/ipfs/%s',
'Dude! For me its blocked in Canada! Not Sweet! Anyways my bro dug up another link to that video, so thats at https://ipfs.io/ipfs/%s',
'Grrr, I got: "Sorry \'about that? This video is not available from my location."(Canada) -- Good news, buddy! I found a link to another copy of the video, https://ipfs.io/ipfs/%s',
'I am the helpful Canadian fixer bot, and it was detected that this video is not available in my country. My friend/guy shared with me this other working link: https://ipfs.io/ipfs/%s'
]

mymessages = [
'If you are getting "not available in your country", Replace the youtube part with "youcan,tube" in any youtube link and watch it. So for example, use this link instead: https://youcan.tube/watch?v=%s',
'I just learned How to View YouTube Videos blocked like this: Step 1: Change the URL of the video you want to watch from "YouTube.com" to "YouCan.Tube", Step 2: Enjoy! Example: https://youcan.tube/watch?v=%s',
'I found a link to this video that\'s not blocked, on some Canadian youtube site: https://youcan.tube/watch?v=%s',
'Yeah, i hate it when the videos are blocked. by changing the "youtube.com" part to "youcan.tube," it should give you a working stream. so for the lazy, it is: https://youcan.tube/watch?v=%s',  #shadowbanned on: 'change "youtube.com" to "youcan.tube"'...
'Yeah no, i hate it when the videos are blocked. by changing the "youtube.com" part to "youcan.tube," it should give you a working stream. so for the lazy, it is: https://youcan.tube/watch?v=%s',  #shadowbanned on: 'change "youtube.com" to "youcan.tube"'...
'I have the same problem. you can view it if you replace the "youtube.com" in the URL with "YouCan.tube". Eg: the URL turns into https://YouCan.Tube/watch?v=%s',
'As a Canadian, that grinds my gears more than anything... I\'ve got some Good news for you, Buddy, you can Use "YouCan.Tube" to unblock the video: https://youcan.Tube/watch?v=%s  (all i did was replace the "youtube.com" with "youcan.tube")'
]



for filename in os.listdir(state_dir):
   #TODO: verify json schema...
   if filename.endswith(".json"):
     try:
       item=json.loads(open(os.path.join(state_dir, filename)).read())
     except FileNotFoundError: #WTF?
       continue
     if 'ipfs_hash' in item:
       for notification in item['notifications']:
         if 'replied' not in notification:
           #2. Notify user:
           randomselection=mymessages[int(random.random()*10) % len(mymessages)] % (item['youtube_id'])
           if 'r/funny' in notification['permalink']:  #because shadowbanned:
             randomselection='a mirror: https://youcan.tube/watch?v=%s' % (item['youtube_id'])
           print ('%s: Will notify %s with message: %s' % (item['youtube_id'], notification['permalink'], randomselection))
           if 'comment_id' in notification:
               comment = reddit.comment(notification['comment_id'])
               comment.reply(randomselection)
           elif 'submission_id' in notification:
               submission = reddit.submission(notification['submission_id'])
               submission.reply(randomselection)
           else:
               print('Alert! Dont know how to notify for: '+notification['permalink'])
           notification['replied']=str(time.time())
           #Update state file:
           filename = '%s/%s.json' % (state_dir, item['youtube_id'])
           thenotifications=item['notifications']
           item=json.loads(open(os.path.join(filename)).read())
           item['notifications']=thenotifications
           open(filename,"w").write(json.dumps(item, indent=4, sort_keys=True))
           #Avoid rate limiting:
           print('Sleeping '+str(delay)+' seconds...')
           time.sleep(delay)

#3. Sleep 20mins...
print ('\033[1mSleeping for 20 minutes...\033[0m')
time.sleep(20 * 60)
