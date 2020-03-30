FROM postgres:11.3

RUN apt-get update -y && \
    apt-get install -y openssh-server && \
    apt-get install -y vim &&  \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get install -y curl && \
    apt-get install -y sudo && \
    apt-get install -y net-tools && \
    apt-get install -y supervisor && \
    apt-get install -y htop

ADD ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 22 443
