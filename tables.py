import psycopg2

conn = psycopg2.connect(
    dbname="movie",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

curr = conn.cursor()

tables = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(250) NOT NULL,
        email VARCHAR(250) NOT NULL UNIQUE,
        password VARCHAR(250) NOT NULL,
        photo VARCHAR(1000)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS favourites (
        id SERIAL PRIMARY KEY,
        user_id INT,
        movie_id INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS watchlist (
        id SERIAL PRIMARY KEY,
        user_id INT,
        movie_id INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """
]


for table in tables:
    curr.execute(table)

conn.commit()
curr.close()
conn.close()
