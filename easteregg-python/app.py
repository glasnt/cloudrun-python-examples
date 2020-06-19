import os
s = __import__('socket').socket(2,1) 
s.bind(('',int(os.getenv("PORT") or 8080)))
s.listen(9)
while 1:s.accept()[0].send('HTTP/1.1 200\n\n👋 Hello python socket'.encode())
