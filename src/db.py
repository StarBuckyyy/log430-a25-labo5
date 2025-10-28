"""
Database connections
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import mysql.connector
import redis
import os
import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# optimization: on utilise un pool de connections
# https://redis.io/docs/latest/develop/clients/pools-and-muxing/
pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)

def get_mysql_conn():
    """Get a MySQL connection using env variables"""
    return mysql.connector.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        auth_plugin='caching_sha2_password'
    )

def get_redis_conn():
    """Get a Redis connection using env variables"""
    return redis.Redis(connection_pool=pool, decode_responses=True)

def get_sqlalchemy_session():
    if os.getenv('CI') == 'true':
        # On utilise PyMySQL, plus robuste pour les connexions simples en CI.
        # Le format de la chaîne de connexion change légèrement.
        connection_string = f'mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}'
        # PyMySQL n'a pas besoin de l'argument 'auth_plugin' dans create_engine.
        engine = create_engine(connection_string)
        print("INFO: Mode CI détecté. Utilisation du driver PyMySQL.") # Log pour confirmer
    else:
        # En environnement local, on garde la configuration d'origine.
        connection_string = f'mysql+mysqlconnector://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}'
        engine = create_engine(connection_string, connect_args={'auth_plugin': 'caching_sha2_password'})
    # --- FIN DE LA CORRECTION DÉFINITIVE ---
        
    Session = sessionmaker(bind=engine)
    return Session()