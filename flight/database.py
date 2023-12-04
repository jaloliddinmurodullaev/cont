import os
import time
import asyncio
import asyncpg
import psycopg2
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ.get('DB_HOST')
PORT = os.environ.get('DB_PORT')
USER = os.environ.get('DB_USER')
PASS = os.environ.get('DB_PASS')
DEFAULT_DB_NAME = os.environ.get('DEFAULT_DB_NAME')

class db_simple():
    def __init__(self):
        self.user = USER
        self.password = PASS
        self.host = HOST
        self.port = PORT
        self.database = DEFAULT_DB_NAME
        self._connection = None
        self._cursor = None
        self.init()

    def connect(self):
        if not self._connection:
            retry_counter = 0
            try:
                self._connection = psycopg2.connect(user = self.user, password = self.password, host = self.host, port = self.port, database = self.database, connect_timeout=3)
                self._connection.autocommit = True
                return self._connection
            
            except psycopg2.OperationalError as error:
                retry_counter += 1
                # ("got error {}. reconnecting {}".format(str(error).strip(), retry_counter))
                time.sleep(5)
                self.connect()
            except psycopg2.DatabaseError as error:
                # ("got error {}. reconnecting {}".format(str(error).strip(), retry_counter))
                conn = psycopg2.connect(user = self.user, password = self.password, host = self.host, port = self.port)
                conn.autocommit = True
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE {DEFAULT_DB_NAME}")
                # ("Created db {DEFAULT_DB_NAME}")
                result = self.execute(f"SELECT datname FROM pg_catalog.pg_database WHERE datname = '{DEFAULT_DB_NAME}'")
                # ("-------------------------- Select --------------------")
                # (result)
                # ("-------------------------- end Select --------------------")
                # if result is None:
                cursor.close()
                conn.close()
                time.sleep(5)
                self.connect()
            except (Exception, psycopg2.Error) as error:
                raise error

    def cursor(self):
        if not self._cursor or self._cursor.closed:
            if not self._connection:
                self.connect()
            self._cursor = self._connection.cursor()
            return self._cursor

    def execute(self, query, *args, retry_counter=0):
        try:
            # self._cursor.execute(query)
            if args:
                self._cursor.execute(query, *args)
                # (f"Execute SQL: {query}, {args}")
            else:
                self._cursor.execute(query)
                # (f"Execute SQL: {query}")
            retry_counter = 0
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as error:
            retry_counter += 1
            # ("got error {}. retrying {}".format(str(error).strip(), retry_counter))
            time.sleep(1)
            self.reset()
            if args:
                self._cursor.execute(query, *args)
                # (f"Execute SQL: {query}, {args}")
            else:
                self._cursor.execute(query)
                # (f"Execute SQL: {query}")
        except (Exception, psycopg2.Error) as error:
            raise error
        try:  
            res = self._cursor.fetchone()
        except psycopg2.ProgrammingError as error:
            res = None
        return res

    def reset(self):
        self.close()
        self.connect()
        self.cursor()

    def close(self):
        if self._connection:
            if self._cursor:
                self._cursor.close()
            self._connection.close()
            # ("PostgreSQL connection is closed")
        self._connection = None
        self._cursor = None

    def init(self):
        self.connect()
        self.cursor()


class db_async():
    def __init__(self):
        self.user = USER
        self.password = PASS
        self.host = HOST
        self.port = PORT
        self.database = DEFAULT_DB_NAME
        self._connection = None

    async def connect(self):
        if not self._connection:
            retry_counter = 0
            while True:
                try:
                    self._connection = await asyncpg.connect(user=self.user, password=self.password, host=self.host,port=self.port, database=self.database)
                    # # (self._connection)
                    return self._connection
                except (Exception, asyncpg.PostgresError) as error:
                    retry_counter += 1
                    # (f"Got error: {str(error).strip()}. Reconnecting {retry_counter}")
                    await asyncio.sleep(5)
                    continue

    async def execute(self, query, *args):
        retry_counter = 0
        while True:
            try:
                await self.connect()
                # await self._connection.execute(query)
                if args:
                    res = await self._connection.execute(query, *args)
                    # (f"Execute SQL: {query}, {args}")
                else:
                    res = await self._connection.execute(query)
                    # (f"Execute SQL: {query}")
                return res
            except Exception as error:
                retry_counter += 1
                # (f"Got error: {str(error).strip()}. Retrying {retry_counter}")
                await asyncio.sleep(1)
                await self.reset()
                continue

    async def fetchval(self, query, *args):
        retry_counter = 0
        while True:
            try:
                await self.connect()
                if args:
                    res = await self._connection.fetchval(query, *args)
                    # (f"Execute SQL: {query}, {args}")
                else:
                    res = await self._connection.fetchval(query)
                    # (f"Execute SQL: {query}")
                return res
            except Exception as error:
                retry_counter += 1
                # (f"Got error: {str(error).strip()}. Retrying {retry_counter}")
                await asyncio.sleep(1)
                await self.reset()
                continue

    async def fetchrow(self, query, *args):
        retry_counter = 0
        while True:
            try:
                await self.connect()
                if args:
                    res = await self._connection.fetchrow(query, *args)
                    # (f"Execute SQL: {query}, {args}")
                else:
                    res = await self._connection.fetchrow(query)
                    # (f"Execute SQL: {query}")
                return res
            except Exception as error:
                retry_counter += 1
                # (f"Got error: {str(error).strip()}. Retrying {retry_counter}")
                await asyncio.sleep(1)
                await self.reset()
                continue

    async def reset(self):
        await self.close()
        await self.connect()

    async def close(self):
        if self._connection:
            await self._connection.close()
            # ("PostgreSQL async connection is closed")
        self._connection = None


