FROM busybox
ENV PORT 8080
CMD while 1; do echo -e "HTTP/1.1 200 OK\n\no/" | nc -l -p $PORT; done
