From silverlogic/python3.6
MAINTAINER wlsdn2215 "jwhyun2215@gmail.com"
COPY . /app
WORKDIR /app

ENTRYPOINT ["python3"]
CMD ["crawl_steam.py"]
