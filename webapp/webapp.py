#!env python3
#https://www.youtube.com/watch?v=Oi-3eRMpOC4
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib,re,tempfile,os,subprocess

class MyHandler(BaseHTTPRequestHandler):
  def print(self, message):
    self.wfile.write(bytes(message, "utf8"))

  #step. 1:
  def do_GET(self):
    self.send_response(200)
    self.log_request()
    self.send_header('Content-type','text/html')
    self.end_headers()
    self.print("""
<HTML>
<HEAD><TITLE>Untitled Document</TITLE></HEAD>
<BODY>
<FORM METHOD=POST>
<INPUT TYPE=TEXT NAME=YouTubeURL><INPUT TYPE=SUBMIT>
</FORM>
</BODY></HTML>
    """)

  #step. 2:
  def do_POST(self):
    self.log_request()
    content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
    post_data = self.rfile.read(content_length) # <--- Gets the data itself
    qsitems=urllib.parse.parse_qs(post_data.decode("utf-8"))
    YouTubeURL=qsitems['YouTubeURL'][0]
    if not re.match('https://www.youtube.com/watch\?v=[\w-]{11}', YouTubeURL):
      self.send_response(400)
      return
    #1. Try to download youtube video using youtube-dl:
    f = tempfile.TemporaryDirectory()
    print(f.name)
    retval=os.system("cd "+f.name+" && youtube-dl "+YouTubeURL) #TODO: stream output to client
    if retval != 0:
      print("Got retval: "+retval);
      self.send_response(500)
      return
    #2. Pin to IPFS and get hash:
    filename=os.listdir(f.name)[0]
    if not re.match('.*\.(?:mkv|mp4|webm)$', filename):
      print('Error - found non matching extension: '+filename)
      self.send_response(500)
      self.end_headers()
      self.print('Error - found non matching extension: '+filename)
      return
    result=subprocess.run(['/root/goproject/bin/ipfs','add', '--quieter', f.name+'/'+filename],stdout=subprocess.PIPE)
    if result.returncode != 0:
      self.send_response(500)
      return
    ipfs_hash = result.stdout.decode("utf-8")
    if not ipfs_hash.startswith('Qm'):
      print('Error - from ipfs add: '+ipfs_hash)
      self.send_response(500)
      return
    self.send_response(200)
    self.send_header('Content-type','text/html')
    self.end_headers()
    self.print("""
<HTML>
<HEAD><TITLE>Untitled Document</TITLE></HEAD>
<BODY>
<A HREF=https://ipfs.io/ipfs/%s>%s</A>
</BODY></HTML>
    """ % (ipfs_hash,ipfs_hash))


#main
server_address = ('0.0.0.0', 8000)
httpd = HTTPServer(server_address, MyHandler)
print('running server...')
httpd.serve_forever()
