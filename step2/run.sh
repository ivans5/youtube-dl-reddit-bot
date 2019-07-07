docker run -d --restart=always -v /state:/state  -v /root/.ipfs:/root/.ipfs -v /root/goproject/bin:/root/goproject/bin step2 python3 -u /step2.py
