import psycopg
from enum import IntEnum, auto


dbname = "somelite"
user = "postgres"
password = "123456"


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
                            user_id integer REFERENCES users(id) ON DELETE CASCADE,
                            name text
                        )
                        """)

            cur.execute("""
                        CREATE TABLE posts (
                            id serial PRIMARY KEY,
                            user_id integer REFERENCES users(id) ON DELETE CASCADE,
                            date text,
                            message text
                        )
                        """)

            cur.execute("""
                        CREATE TABLE relationships (
                            user_id_1 integer REFERENCES users(id) ON DELETE CASCADE,
                            user_id_2 integer REFERENCES users(id) ON DELETE CASCADE,
                            PRIMARY KEY (user_id_1, user_id_2),
                            CHECK (user_id_1 < user_id_2),
                            type integer
                        )
                        """)

            insert_placeholder_data(cur)


def insert_placeholder_data(cur):
    create_new_user(cur, "Alice", "password1", 30)
    create_new_user(cur, "Bob", "password2", 35)
    create_new_user(cur, "Charlie", "password3", 25)
    create_new_user(cur, "David", "password4", 40)
    create_new_user(cur, "DELETEME", "password5", 99)

    # Inserting data into the 'groups' table
    cur.execute("INSERT INTO groups (user_id, name) VALUES (%s, %s)", (1, "Staff"))
    cur.execute("INSERT INTO groups (user_id, name) VALUES (%s, %s)", (2, "Student"))
    cur.execute("INSERT INTO groups (user_id, name) VALUES (%s, %s)", (3, "Alumni"))

    # Inserting data into the 'posts' table
    add_post(cur, 1, "June 1, 2024", "Hello, world!")
    add_post(cur, 2, "May 22, 2024", "This is a test post.")
    add_post(cur, 3, "May 30, 2024", "Welcome to my domain!")
    add_post(cur, 4, "May 30, 2024", "Test post, please ignore")
    add_post(cur, 5, "Today yaal", "IF YOU SEE ME, SOMETHING IS WRONG")
    delete_user(cur, 5)

    # Adding a relationship
    add_relation(1, 2, Relation.friends)
    add_relation(1, 3, Relation.friends)

    # Removing a relationship
    # remove_relation(1, 2)
    # remove_relation(1,3)


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
                    SELECT user_id_1
                    FROM relationships
                    WHERE user_id_2 = %(id)s
                )
                OR posts.user_id IN (
                    SELECT user_id_2
                    FROM relationships
                    WHERE user_id_1 = %(id)s
                );
            """,
                {"id": id},
            )
            return cur.fetchall()
        
def create_new_user(curx, namex, passwordx, agex):
    curx.execute(
    "INSERT INTO users (name, password, age) VALUES (%s, %s, %s)",
    (namex, passwordx, agex),
    )

def delete_user(curx, idx):
    curx.execute(
    "DELETE FROM users WHERE id = %s",
    (idx,)
    )

def add_post(curx, idx, datex, messagex):
    curx.execute(
    "INSERT INTO posts (user_id, date, message) VALUES (%s, %s, %s)",
    (idx, datex, messagex),
    )

def add_relation(user_id_1, user_id_2, relation_type):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO relationships (user_id_1, user_id_2, type) VALUES (%s, %s, %s)",
                (user_id_1, user_id_2, relation_type),
            )

def remove_relation(user_id_1, user_id_2):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM relationships WHERE user_id_1 = %s AND user_id_2 = %s",
                (user_id_1, user_id_2),
            )