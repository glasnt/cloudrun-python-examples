FROM python:3.7-slim

ENV APP_HOME /app
ENV PORT 8080
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .
EXPOSE $PORT
WORKDIR $APP_HOME

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD twistd -n web --class=hello.resource --port "tcp:port=${PORT}" 
