FROM python:3.10

WORKDIR /app

ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_USER=postgres
ENV DB_PASS=1111

ENV DEFAULT_DB_NAME=test_content

ENV CACHE_HOST=localhost
ENV CACHE_PORT=6379

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt

COPY . /usr/src/app

EXPOSE 8000

CMD ['python3', 'run.py', 'migrate']
CMD ['python3', 'run.py', 'runserver']