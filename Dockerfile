FROM debian:stretch

# ENV variables
ENV TZ=Etc/UTC

# Debian packages
RUN apt-get update -yqq && \
    apt-get install -yqq python3-pip python3-dev && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get install -yqq nginx && \
    apt-get -yqq install uwsgi-plugin-python3 && \
    apt-get install -yqq libpq-dev python3-dev && \
    apt-get install -yqq uwsgi && \
    apt-get install -yqq vim && \
    apt-get install -yqq curl && \
    apt-get install -yqq sudo && \
    apt-get install -yqq git && \
    apt-get install -yqq net-tools  && \
    apt-get install -yqq openssh-server && \
    apt-get install -yqq postgresql postgresql-contrib && \
    apt-get install -yqq supervisor && \
    apt-get install -yqq zip && \
    apt-get install -yqq htop

# ADD USER
RUN adduser --disabled-password --gecos '' rh && \
    usermod -aG sudo rh && \
    mkdir -p  /var/run/sshd /var/log/supervisor /etc/postgresql /var/log/postgresql /var/lib/postgresql && \
    echo 'rh ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    echo 'rh:gbf123' | chpasswd && \
    echo 'root:gbf123' | chpasswd && \
    sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# CHANGE USER
USER root

# MOVE TO WORKING DIRECTORY
WORKDIR /app

# COPY ALL
ADD . /app

# PIP PACKAGES
RUN pip3 install -r requirements.txt
RUN git clone https://github.com/reingart/pyfpdf.git

# INSTALL PYFPDF
WORKDIR /app/pyfpdf
RUN sudo python3 setup.py install

WORKDIR /app

# REMOVE DEFAULT IN NGINX
RUN sudo rm /etc/nginx/sites-available/default
RUN sudo rm /etc/nginx/sites-enabled/default

RUN sudo mv api.ini /etc/uwsgi/apps-available/api.ini
RUN sudo mv rh_api /etc/nginx/sites-available/rh_api

# SYMLINK
RUN sudo ln -s /etc/uwsgi/apps-available/api.ini /etc/uwsgi/apps-enabled/api.ini
RUN sudo ln -s /etc/nginx/sites-available/rh_api /etc/nginx/sites-enabled/rh_api

WORKDIR /app
ADD ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf


EXPOSE 22 443
CMD ["/usr/bin/supervisord"]