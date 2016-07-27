FROM ubuntu:14.04.4

# install python dependencies
RUN apt-get update && apt-get install -y python2.7 python-pip python-virtualenv git net-tools build-essential httpd httpd-devel

# clone the webapp
RUN git clone https://github.com/loeh/e2eTurtlebotWebApp.git /webapp

RUN cd /webapp
RUN virtualenv flask
RUN flask/bin/pip install flask requests enum34

EXPOSE 5000

WORKDIR /webapp

# run it
CMD ./app.py
