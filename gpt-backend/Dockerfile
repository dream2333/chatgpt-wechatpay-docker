FROM python:3.11-alpine
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY ./requirements.txt ./
RUN pip --no-cache-dir install -r requirements.txt
COPY . ./

CMD ["sh", "/app/run.bash"]