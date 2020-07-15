FROM python:3.7-slim

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

ENV FUNCTION_TARGET function

RUN pip install gunicorn functions-framework
RUN pip install -r requirements.txt

CMD exec functions-framework
