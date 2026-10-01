FROM python:3.12-alpine

RUN addgroup -S media && adduser -S -G media media
WORKDIR /app
COPY server.py /app/server.py
RUN mkdir /data && chown media:media /data
USER media
EXPOSE 8080
CMD ["python", "-u", "/app/server.py"]
