import psycopg
from enum import IntEnum, auto


dbname = "somelite"
user = "postgres"
password = "postgres"


class Relation(IntEnum):
    friends = auto()


def connect():
    return psycopg.connect("dbname={} user={} password={}".format(dbname, user, password))


def recreate():
    with psycopg.connect("dbname={} user={} password={}".format("postgres", user, password)) as conn:
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

            cur.execute("""
                        CREATE TABLE relationships (
                            user_id_1 integer REFERENCES users(id),
                            user_id_2 integer REFERENCES users(id),
                            PRIMARY KEY (user_id_1, user_id_2),
                            CHECK (user_id_1 < user_id_2),
                            type integer
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
    cur.execute(
        "INSERT INTO relationships (user_id_1, user_id_2, type) VALUES (%s, %s, %s)",
        (1, 2, Relation.friends),
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


def get_posts_of_friends(id):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT users.name, posts.date, posts.message
                FROM posts
                JOIN users
                ON posts.user_id = users.id
                WHERE posts.user_id IN (
                SELECT CASE
                    WHEN user_id_1 = %(id)s THEN user_id_2
                    ELSE user_id_1
                END AS other_user_id
                FROM relationships
                WHERE user_id_1 = %(id)s
                    OR user_id_2 = %(id)s
            );
            """,
                {"id": id},
            )
            return cur.fetchall()
