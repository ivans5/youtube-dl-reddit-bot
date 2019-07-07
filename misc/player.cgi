#!/bin/env python3

# Import modules for CGI handling 
import cgi, cgitb 
import re
import requests,json

# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields
v = form.getvalue('v')
if not re.match('[\w-]{11}$', v):
    raise Error("Error")

print ("Content-type:text/html\r\n\r\n")

#1.lookup Qm  ipfs_hash:
try:
  ipfs_hash=json.loads(requests.get('http://68.183.174.68:8081/%s.json' % (v)).text)['ipfs_hash']
except:
  ipfs_hash='QmRqUYeHDGBdHviCiuxitd117BdDDyztpsxivV9QJBkFMo'

#2. get title:
title=re.search('<title>(.*?)</title>',requests.get('https://youtube.com/watch?v='+v).text,re.I).group(1).replace(" - YouTube","")

print ("""
<html><head><title>%s - YouCan.Tube</title>
<meta charset="UTF-8">
<STYLE>
h1 {
  font-family: "Arial"
}
div.d1 {
  background-color: black;
  min-width: 640px;
  min-height: 480px;
  display: inline-block;
}
</STYLE>
</head>
<body onLoad="function f(){document.getElementById('player').play();} f(); setTimeout(f, 3000);">
<DIV><IMG SRC=/top.png></DIV>
<DIV CLASS="d1">
<video controls autoplay="autoplay" id="player" preload="auto">
  <source src="http://gateway.ipfs.org.uk:8080/ipfs/%s">
Your browser does not support the video tag.
</video>
<!-- <SPAN CLASS="s1"><FONT COLOR=WHITE>sometext</FONT></SPAN> -->
</DIV>
<DIV><H1 STYLE="font: arial">%s</H1><IMG SRC=/bottom.png></DIV>
</body>
</html>
""" % (title, ipfs_hash, title))

