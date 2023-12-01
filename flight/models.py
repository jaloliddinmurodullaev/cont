import json
import uuid
from .database import db_simple, db_async

def create_database():
    db = db_simple()
          
    create_table_query_offers = f'''
        CREATE TABLE IF NOT EXISTS offers (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            system_id UUID NOT NULL,
            provider_id UUID NOT NULL,
            provider_name VARCHAR(255),
            departure VARCHAR(255),
            arrival VARCHAR(255),
            departure_date VARCHAR(255),
            airline VARCHAR(255),
            offer JSONB
        );
    '''

    create_table_query_systems = f'''
        CREATE TABLE IF NOT EXISTS systems (
            id SERIAL PRIMARY KEY,
            system_id UUID NOT NULL UNIQUE,
            system_name VARCHAR(255),
            system_type VARCHAR(255),
            auth_data_fields JSONB
        );
    '''

    create_table_query_integrations = f'''
        CREATE TABLE IF NOT EXISTS integrations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            integration_class VARCHAR(255),
            system_id UUID NOT NULL UNIQUE
        );
    '''

    create_table_query_admins = f'''
        CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        );
    '''

    create_table_query_search = f'''
        CREATE TABLE IF NOT EXISTS search (
            id SERIAL PRIMARY KEY,
            request_id UUID,
            adt INT,
            chd INT,
            inf INT,
            class VARCHAR(50),
            direct BOOLEAN,
            flexible BOOLEAN,
            currency VARCHAR(3),
            directions JSONB
        );
    '''

    create_table_query_offer = f'''
        CREATE TABLE IF NOT EXISTS offer (
            offer_id UUID PRIMARY KEY,
            search INT REFERENCES search(id),
            offer_data JSONB,
            other JSONB,
            provider_id UUID,
            provider_name VARCHAR(400),
            system_id UUID
        );
    '''

    create_table_query_orders = f'''
        CREATE TABLE IF NOT EXISTS orders (
            order_id UUID PRIMARY KEY,
            offer UUID REFERENCES offer(offer_id),
            status VARCHAR(100),
            agent_id UUID,
            system_name VARCHAR(300),
            order_number INT,
            pnr_number VARCHAR(100),
            passengers JSONB,
            booking_response JSONB
        );
    '''
    
    # Create tables
    db.execute(create_table_query_offers)
    db.execute(create_table_query_systems)
    db.execute(create_table_query_integrations)
    db.execute(create_table_query_admins)
    db.execute(create_table_query_search)
    db.execute(create_table_query_offer)
    db.execute(create_table_query_orders)
    db.close()

async def insert_search(search_data):
    _db = db_async()
    insert_query = "INSERT INTO search (request_id, adt, chd, inf, class, direct, flexible, currency, directions) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"
    directions = {
        "directions": search_data['directions']
    }
    await _db.execute(insert_query, search_data['request_id'], search_data['adt'], search_data['chd'], search_data['inf'], search_data['class'], search_data['direct'], search_data['flexible'], search_data['currency'], json.dumps(directions))

    select_query = f"SELECT id FROM search WHERE request_id = $1"
    search = await _db.fetchval(select_query, search_data['request_id'])
    await _db.close()

    return search if search else None

async def insert_offer(offer_id, search_object, offer_data, other, provider_id, provider_name, system_id):
    print(offer_id)
    _db = db_async()

    insert_query = "INSERT INTO offer (offer_id, search, offer_data, other, provider_id, provider_name, system_id) VALUES ($1, $2, $3, $4, $5, $6, $7)"

    await _db.execute(insert_query, offer_id, search_object, json.dumps(offer_data), json.dumps(other), provider_id, provider_name, system_id)

    select_query = f"SELECT offer_id FROM offer WHERE offer_id = $1"

    offer = await _db.fetchval(select_query, offer_id)

    await _db.close()

    return offer if offer else None

async def insert_order(order_id, offer, status, agent_id, system_name, order_number, pnr_number, passengers, booking_response):
    _db = db_async()

    insert_query = "INSERT INTO orders (order_id, offer, status, agent_id, system_name, order_number, pnr_number, passengers, booking_response) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"

    await _db.execute(insert_query, order_id, offer, status, agent_id, system_name, order_number, pnr_number, json.dumps(passengers), json.dumps(booking_response))

    await _db.close()

async def get_order(order_number):
    _db = db_async()

    select_query = f"SELECT * FROM orders WHERE order_number = $1"

    order = await conn.fetchrow(select_query, order_number)

    order = dict(order)

    order['booking_response'] = copy.deepcopy(json.loads(order['booking_response']))
    order['booking_response']['status'] = copy.deepcopy(order['status'])

    await _db.close()

    return order['booking_response']

async def update_order(order_number, order_status_code):
    _db = db_async()

    select_query = f"UPDATE orders SET status = $2 WHERE order_number = $1"

    try:
        order = await _db.execute(select_query, order_number, order_status_code)
    except Exception as e:
        print(str(e))

    await _db.close()

    return order

async def get_orders_count():
    _db = db_async()

    select_query = "SELECT COUNT(*) FROM orders;"

    count = await _db.execute(select_query)

    print(count)

    await _db.close()

    return count

def create_admin(username='admin', password='admin'):
    db = db_simple()
    try:
        insert_query = "INSERT INTO admins (username, password) VALUES ($1, $2)"
        db.execute(insert_query, username, password)
    except Exception as e:
        print(e)
    db.close()
 
def change_admin_username_and_password(username, password):
    pass # yet to update
 
def get_admin(username, password):
    db = db_simple()
    response = {
        'status': 'success',
        'message': 'username and password are correct'
    }

    try:
        select_query = f"SELECT username, password FROM admins WHERE username = $1 and password = $2"
        db.execute(select_query, username, password)
    except Exception as e:
        response['status'] = 'error',
        response['message'] = 'username and password are not correct'
        print(e)
    db.close()

    return response
 
async def insert_data(system_id, provider_id, provider_name, offers):
    _db = db_async()
    
    insert_query = "INSERT INTO offers (system_id, provider_id, provider_name, offer) VALUES ($1, $2, $3, $4)"
    
    for offer in offers['data']:
        await _db.execute(insert_query, uuid.UUID(system_id), uuid.UUID(provider_id), provider_name, json.dumps(offer))
    
    await _db.close()

async def insert_system(system_id, system_name, system_type, auth_data_fields):
    result = {
        'status': 'success',
        'message': 'new system successfully has been added'
    }
    _db = db_async()
    try:       
        insert_query = "INSERT INTO systems (system_id, system_name, system_type, auth_data_fields) VALUES ($1, $2, $3, $4)"
        await _db.execute(insert_query, uuid.UUID(system_id), system_name, system_type, json.dumps({"fields": auth_data_fields}))

    except Exception as e:
        result['status']  = 'error'
        result['message'] = 'error adding a new system'
        print(e)

    finally:
        await _db.close()
        return result

async def get_system_name(system_id):
    _db = db_async()

    select_query = f"SELECT system_name FROM systems WHERE system_id = $1"

    system_name = await _db.fetchval(select_query, uuid.UUID(system_id))

    await _db.close()
    
    return system_name if system_name else None

