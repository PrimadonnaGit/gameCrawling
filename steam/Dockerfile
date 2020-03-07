From silverlogic/python3.6
MAINTAINER wlsdn2215 "jwhyun2215@gmail.com"
RUN sudo apt-get update -y
RUN mkdir -p /app/data/steam
COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["crawl_steam.py"]
