FROM python:3.8

ENV  HOME /root
WORKDIR /root
COPY . .
RUN pip install -r requirements.txt
# ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
# RUN chmod +x /wait
CMD  python3 -u server.py