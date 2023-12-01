FROM python:3.11 as compiler
ENV PYTHONUNBUFFERED 1

RUN mkdir content
WORKDIR /content/

RUN python3 -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

# install requirements
RUN pip install --upgrade pip
COPY ./requirements.txt /content/requirements.txt
RUN pip install -Ur requirements.txt

EXPOSE 8028

COPY . /content/