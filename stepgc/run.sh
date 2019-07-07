docker run -d --restart=always -v /state:/state  -v /root/.ipfs:/root/.ipfs -v /root/goproject/bin:/root/goproject/bin stepgc python3 -u /stepgc.py
