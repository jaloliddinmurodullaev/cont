FROM python:3.10.6

RUN mkdir app
COPY . /app
WORKDIR /app

# Setting environment variables
ENV PYTHONUNBUFFERED 1
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_USER=postgres
ENV DB_PASS=1111
ENV DEFAULT_DB_NAME=content

ENV CACHE_HOST=redis
ENV CACHE_PORT=6379

# Installing requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Database migration
# RUN python run.py migrate

# Running the app
# CMD ["python", "run.py", "runserver"]