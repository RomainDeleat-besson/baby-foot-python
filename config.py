from urllib.parse import urlparse

ENV = "prod"

if ENV == 'dev':
    DATABASE_CONFIG = {
        'host': "localhost",
        'database': "babyfoot",
        'user': "postgres",
        'password': ""
    }
else: 

    uri = "****"
    parsed_uri = urlparse(uri)

    DATABASE_CONFIG = {
        'host': "localhost",
        'database': "babyfoot",
        'user': "adminbabyfoot",
        'password': "0000",
        'port': "5432"
    } 
