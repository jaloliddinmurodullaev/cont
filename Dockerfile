FROM python:3.10.6

RUN mkdir app
COPY . /app
WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV DB_HOST=172.19.0.3
ENV DB_PORT=5432
ENV DB_USER=postgres
ENV DB_PASS=1111
ENV DEFAULT_DB_NAME=test_content

ENV CACHE_HOST=172.19.0.2
ENV CACHE_PORT=6379

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "run.py", "migrate"]
CMD ["python", "run.py", "runserver"]