
# bigwordbot

import praw
import requests,re,json,os,time

# create the objects from the imported modules

# reddit api login
reddit = praw.Reddit(client_id='REDACTED',
                     client_secret='rEDACTED',
                     user_agent='my user agent')

subreddits = ['normmacdonald','nathanforyou','documentaries','television','worldnews','gaming','music','videos',
'conan', 'enoughmuskspam', 'enoughpetersonspam', 'futureman', 'futurology', 'gadgets', 'stockmarket', 
'getmotivated', 'history', 'listentothis', 'movies', 'news', 'nottheonion', 'science', 'space', 'upliftingnews',
'southpark','reno911','funny', 'dailyshow', 'space', 'jimjefferies', 'BroadCity', 'AskReddit', 'workaholics','movies']


submission_max_age = 6 * 86400
mylimit = None
#'blocked', inaccessible, not.*avaiable, or your/my country
blocked_pattern = '(?:blocked|inaccessible|not.{,20}available|(?:my|your)\s+country)'
dont_reply_to_list = ['YourName','YourName2']

subreddit_stats={}
def update_subreddit_stats(item):
    for x in item.keys(): subreddit_stats[x]+=item[x]

#Examine sometext and possibly create a new state event json file about it..
#returns a list of matching videoids...
def examine(sometext,permalink):
    #print('examining some text:'+sometext)
    retval=[]
    videos_found=0
    videoids=re.findall('youtube.com/watch\?v=([\w-]{11})',sometext) + re.findall('youtu.be/([\w-]{11})',sometext)
    for videoid in videoids:
      #print('Checking: '+videoid)
      text1=requests.get('https://www.youtube.com/get_video_info?video_id='+videoid).text
      if 'reason=The+uploader+has+not+made+this+video+available+in+your+country' in text1:
        print("    \033[1m\u2193 %s FOUND ONE: %s\033[0m" % (permalink,videoid))
        videos_found = videos_found + 1
        filename='state/%s.json' % (videoid)
        retval.append(videoid)
        #TODO: restore the old behaviour and schedule a notification directly in some % of cases (and use a different pool of messages when sending)...
        if os.path.isfile(filename):
          print ('    Notice: '+videoid+', already the file exists, updating references...')
          #Update the references:
          item=json.loads(open(os.path.join(filename)).read())
          if 'references' not in item: item['references'] = [] #legacy
          if permalink not in item['references']:
             item['references'].append(permalink)
          open(filename,"w").write(json.dumps(item, indent=4, sort_keys=True))
          continue
        output={'notifications': [],
                'created': time.time(), 
                'youtube_id': videoid, 
                'references': [permalink]
        }
        print ("    creating file: "+filename)
        open(filename,"w").write(json.dumps(output, indent=4, sort_keys=True))
    update_subreddit_stats({'bytes_read': len(sometext), 'videos_found': videos_found, 'videos_checked': len(videoids)})
    return retval

def recurseForest(forest, videoid):
   for top_level_comment in forest:
      if not isinstance(top_level_comment, praw.models.MoreComments): #TODO: expand these...
          newvideoid=None
          if videoid and re.search(blocked_pattern, top_level_comment.body, re.I):
               if isinstance(top_level_comment.author, praw.models.reddit.redditor.Redditor) and top_level_comment.author.name not in dont_reply_to_list:
                   print ('      \033[32mpattern match from %s! permalink=%s, body=%s\033[0m' % (top_level_comment.author.name, top_level_comment.permalink, top_level_comment.body))
                   notify(top_level_comment, videoid) 
                   #Dont bother doing examine() for this comment...
          else:
               newvideoids=examine(top_level_comment.body, top_level_comment.permalink) 
               newvideoid=newvideoids[0] if newvideoids else None #TODO: deal with multiple videos better...
          recurseForest(top_level_comment.replies, newvideoid)

def notify(comment, videoid):
   notificationinfo = { 'permalink': comment.permalink, 'comment_id': comment.id }
   filename='state/%s.json' % (videoid)
   #Open file and add to notifications list:
   item=json.loads(open(filename).read())
   if notificationinfo['permalink'] not in [x['permalink'] for x in item['notifications']]:
      #TODO: skip notifying if this is a smaller submission AND we have notified enough times forthe number of top-level posts...
      item['notifications'].append(notificationinfo)
      open(filename,"w").write(json.dumps(item, indent=4, sort_keys=True))
      print ("      Notification added: comment=%s, videoid=%s\n" % (str(comment), videoid))
      update_subreddit_stats({'notifications_new': 1})
   else:
      print ("      Notification already existed! comment=%s, videoid=%s\n" % (str(comment), videoid))
      update_subreddit_stats({'notifications_skipped': 1})

#try:  #TODO: use commentids instead for the cache (and a gdb/lmdb) (so that you can revisit the same submissions)...
#  submissionskipcache=open('state/submissions.txt').readlines()
#except:
#  submissionskipcache=[]
for subreddit in subreddits:
  #print ('Starting subreddit: '+subreddit)
  subreddit_stats={'bytes_read': 0, 'videos_found': 0, 'videos_checked': 0, 'skipped_total': 0, 'skipped_too_old': 0, 'notifications_new': 0, 'notifications_skipped': 0} 
  for submission in reddit.subreddit(subreddit).hot(limit=mylimit):
      too_old=time.time() - submission.created_utc > submission_max_age
      if not too_old: #and submission.id+"\n" not in submissionskipcache
        videoids=examine(submission.url, submission.permalink)
        recurseForest(submission.comments, videoids[0] if videoids else None)
        #Update cache on disk:
        #open('state/submissions.txt', 'a').write(submission.id+"\n") #update cache
      else:
        #print ('Skipping '+submission.id+' (already in cache? too_old='+str(too_old)+')!!')
        #TODO: use update_stats({'skipped_total': 1}) instead...
        subreddit_stats['skipped_total'] = subreddit_stats['skipped_total'] + 1
        if too_old: subreddit_stats['skipped_too_old'] = subreddit_stats['skipped_too_old'] + 1
  print ('r/%s: %s' % (subreddit, str(subreddit_stats)))

print ('\033[1mSleeping for 20 minutes...\033[0m')
time.sleep(20 * 60)
