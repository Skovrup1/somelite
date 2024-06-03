import psycopg
from psycopg import errors


dbname = "somelite"
user = "postgres"


def connect():
    return psycopg.connect("dbname={} user={}".format(dbname, user))


def recreate():
    with psycopg.connect("dbname={} user={}".format("postgres", user)) as conn:
        conn.autocommit = True

        with conn.cursor() as cur:
            try:
                cur.execute("DROP DATABASE {}".format(dbname))
            except psycopg.ProgrammingError:
                pass

            cur.execute("CREATE DATABASE {}".format(dbname))


def create():
    recreate()

    with connect() as conn:
        conn.autocommit = True

        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE users (
                            id serial PRIMARY KEY,
                            name text,
                            password text,
                            age integer
                        )
                        """)

            cur.execute("""
                        CREATE TABLE groups (
                            id serial PRIMARY KEY,
                            user_id integer REFERENCES users(id),
                            name text
                        )
                        """)

            cur.execute("""
                        CREATE TABLE posts (
                            id serial PRIMARY KEY,
                            user_id integer REFERENCES users(id),
                            date text,
                            message text
                        )
                        """)

            insert_placeholder_data(cur)


def insert_placeholder_data(cur):
    cur.execute(
        "INSERT INTO users (name, password, age) VALUES (%s, %s, %s)",
        ("Alice", "password1", 30),
    )
    cur.execute(
        "INSERT INTO users (name, password, age) VALUES (%s, %s, %s)",
        ("Bob", "password2", 35),
    )
    cur.execute(
        "INSERT INTO users (name, password, age) VALUES (%s, %s, %s)",
        ("Charlie", "password3", 25),
    )

    # Inserting data into the 'groups' table
    cur.execute("INSERT INTO groups (user_id, name) VALUES (%s, %s)", (1, "Staff"))
    cur.execute("INSERT INTO groups (user_id, name) VALUES (%s, %s)", (2, "Student"))
    cur.execute("INSERT INTO groups (user_id, name) VALUES (%s, %s)", (3, "Alumni"))

    # Inserting data into the 'posts' table
    cur.execute(
        "INSERT INTO posts (user_id, date, message) VALUES (%s, %s, %s)",
        (1, "June 1, 2024", "Hello, world!"),
    )
    cur.execute(
        "INSERT INTO posts (user_id, date, message) VALUES (%s, %s, %s)",
        (2, "May 22, 2024", "This is a test post."),
    )
    cur.execute(
        "INSERT INTO posts (user_id, date, message) VALUES (%s, %s, %s)",
        (3, "May 30, 2024", "Welcome to my domain!"),
    )


def get_users():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users")

            return cur.fetchall()


def get_posts():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT users.name, posts.date, posts.message
                        FROM users
                        JOIN posts ON users.id = posts.user_id;
                        """)

            return cur.fetchall()
