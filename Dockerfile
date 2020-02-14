# vim:set ft=dockerfile:
FROM python:3.7
MAINTAINER Matija Pretnar <matija.pretnar@fmf.uni-lj.si>

# Secret key is only here to make collectstatic work.
# It is overrided from settings in docker-compose.
ENV SECRET_KEY=very_secret_key

# Add Tomo user and group first to make sure their IDs get assigned consistently
RUN groupadd -r tomo && useradd -r -g tomo tomo

# Install required packages
RUN apt-get update
RUN apt-get install -y \
  git \
  libpython3-dev \
  libsasl2-dev \
  locales \
  libldap2-dev \
  libsasl2-dev \
  libssl-dev

RUN rm -rf /var/lib/apt/lists/*


RUN sed -i "/^# sl_SI.UTF-8 UTF-8/ c sl_SI.UTF-8 UTF-8" /etc/locale.gen
RUN sed -i "/^# de_DE.UTF-8 UTF-8/ c de_DE.UTF-8 UTF-8" /etc/locale.gen
RUN locale-gen
RUN update-locale
WORKDIR /home/tomo

# Copy cloned repository
COPY web projekt-tomo/web

# Install dependencies
RUN pip install -U pip wheel setuptools
RUN pip install -r projekt-tomo/web/requirements/arnes.txt

ENV SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=very_secret_key
ENV SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=very_secret_key
ENV SOCIAL_AUTH_FACEBOOK_KEY=very_secret_key
ENV SOCIAL_AUTH_FACEBOOK_SECRET=very_secret_key

RUN python projekt-tomo/web/manage.py collectstatic --noinput --settings=web.settings.arnes
RUN chown tomo.tomo -R /home/tomo

# UWSGI options are read from environmental variables.
# They are specified in docker-compose file.
CMD ["uwsgi"]
