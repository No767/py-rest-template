FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  tini \
  && apt-get clean

WORKDIR /template
COPY /server /template/server/
COPY /requirements.txt /template/requirements.txt

RUN adduser --disabled-password --gecos "" template \
  && chown -R template:template /template

USER template

ENV PATH="${PATH}:/home/template/.local/bin"

RUN pip install --user -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["python3", "/template/server/launcher.py", "--no-workers"]

STOPSIGNAL SIGTERM