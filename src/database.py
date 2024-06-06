import psycopg
from enum import IntEnum, auto


class Relation(IntEnum):
    friends = auto()


class Db:
    def __init__(self, name, password, user, postgres_password):
        self.name = name
        self.user = user
        self.password = password
        self.postgres_password = postgres_password

    def delete(self):
        with psycopg.connect(
            "dbname={} user={} password={}".format(
                "postgres", self.user, self.postgres_password
            )
        ) as conn:
            conn.autocommit = True

            with conn.cursor() as cur:
                try:
                    cur.execute("DROP DATABASE {}".format(self.name))
                except psycopg.ProgrammingError:
                    pass

    def create(self):
        with psycopg.connect("dbname={} user={}".format("postgres", self.user)) as conn:
            conn.autocommit = True

            with conn.cursor() as cur:
                cur.execute("CREATE DATABASE {}".format(self.name))

    def connect(self):
        return psycopg.connect(
            "dbname={} user={} password={}".format(
                self.name, self.user, self.password
            )
        )

    def create_tables(self):
        with self.connect() as conn:
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

                cur.execute("""
                            CREATE TABLE group_memberships (
                                user_id integer REFERENCES users(id) ON DELETE CASCADE,
                                group_id integer REFERENCES groups(id) ON DELETE CASCADE,
                                PRIMARY KEY (user_id, group_id)
                            )
                            """)

                cur.execute("""
                            CREATE TABLE likes (
                                user_id integer REFERENCES users(id) ON DELETE CASCADE,
                                post_id integer REFERENCES posts(id) ON DELETE CASCADE,
                                PRIMARY KEY (user_id, post_id)
                            )
                            """)

                self.insert_placeholder_data(cur)

    def create_new_user(curx, namex, passwordx, agex):
        curx.execute(
            "INSERT INTO users (name, password, age) VALUES (%s, %s, %s)",
            (namex, passwordx, agex),
        )

    def add_post(self, curx, idx, datex, messagex):
        curx.execute(
            "INSERT INTO posts (user_id, date, message) VALUES (%s, %s, %s)",
            (idx, datex, messagex),
        )

    def delete_user(self, curx, idx):
        curx.execute("DELETE FROM users WHERE id = %s", (idx,))

    def get_users(self):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users")

                return cur.fetchall()

    def get_posts(self):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            SELECT users.name, posts.date, posts.message
                            FROM users
                            JOIN posts ON users.id = posts.user_id;
                            """)

                return cur.fetchall()

    def get_posts_of_friends(self, id):
        with self.connect() as conn:
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

    def add_relation(self, user_id_1, user_id_2, relation_type):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO relationships (user_id_1, user_id_2, type) VALUES (%s, %s, %s)",
                    (user_id_1, user_id_2, relation_type),
                )

    def insert_placeholder_data(self, cur):
        Db.create_new_user(cur, "Alice", "password1", 30)
        Db.create_new_user(cur, "Bob", "password2", 35)
        Db.create_new_user(cur, "Charlie", "password3", 25)
        Db.create_new_user(cur, "David", "password4", 40)
        Db.create_new_user(cur, "DELETEME", "password5", 99)

        # Inserting data into the 'groups' table
        cur.execute("INSERT INTO groups (user_id, name) VALUES (%s, %s)", (1, "Staff"))
        cur.execute(
            "INSERT INTO groups (user_id, name) VALUES (%s, %s)", (2, "Student")
        )
        cur.execute("INSERT INTO groups (user_id, name) VALUES (%s, %s)", (3, "Alumni"))

        # Inserting data into the 'posts' table
        self.add_post(cur, 1, "June 1, 2024", "Hello, world!")
        self.add_post(cur, 2, "May 22, 2024", "This is a test post.")
        self.add_post(cur, 3, "May 30, 2024", "Welcome to my domain!")
        self.add_post(cur, 4, "May 30, 2024", "Test post, please ignore")
        self.add_post(cur, 5, "Today yaal", "IF YOU SEE ME, SOMETHING IS WRONG")
        self.delete_user(cur, 5)

        # Adding a relationship
        self.add_relation(1, 2, Relation.friends)
        self.add_relation(1, 3, Relation.friends)

        # # Removing a relationship
        # remove_relation(1, 2)
        # remove_relation(1,3)

        # Adding some likes
        self.like_post(1, 1)
        self.like_post(1, 1)
        self.like_post(2, 1)
        self.like_post(1, 2)
        self.like_post(3, 1)
        self.like_post(2, 3)
        self.like_post(1, 4)

        # Testing show_all_likes function
        print("Number of likes for post 1:", self.show_all_likes(1))
        print("Number of likes for post 2:", self.show_all_likes(2))
        print("Number of likes for post 3:", self.show_all_likes(3))
        print("Number of likes for post 4:", self.show_all_likes(4))

        # Testing regular_match function
        print("Posts matching 'world':", self.regular_match("world"))
        print("Posts matching 'world':", self.regular_match("WORLD"))
        print("Posts matching 'world':", self.regular_match("hello world"))
        print("Posts matching 'world':", self.regular_match("test world"))

    def remove_relation(self, user_id_1, user_id_2):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM relationships WHERE user_id_1 = %s AND user_id_2 = %s",
                    (user_id_1, user_id_2),
                )

    def add_group(curx, owner_id, namex):
        curx.execute(
            "INSERT INTO groups (user_id, name) VALUES (%s, %s)", (owner_id, namex)
        )

    def delete_group(curx, owner_id):
        curx.execute("DELETE FROM groups WHERE user_id = %s", (owner_id,))

    def join_group(curx, user_id, group_id):
        curx.execute(
            "INSERT INTO group_memberships (user_id, group_id) VALUES (%s, %s)",
            (user_id, group_id),
        )

    def leave_group(curx, user_id, group_id):
        curx.execute(
            "DELETE FROM group_memberships WHERE user_id = %s AND group_id = %s",
            (user_id, group_id),
        )

    def like_post(self, user_id, post_id):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO likes (user_id, post_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",  # if a duplicate like is attempted, the insertion is ignored
                    (user_id, post_id),
                )

    def show_all_likes(self, post_id):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                            SELECT COUNT(likes.user_id) AS like_count
                            FROM likes
                            WHERE likes.post_id = %s;
                            """,
                    (post_id,),
                )
                return cur.fetchone()[0]

    def regular_match(self, keyword):
        with self.connect() as conn:
            with conn.cursor() as cur:
                words = keyword.split()
                pattern = "|".join(words)
                query = """
                    SELECT users.name, posts.date, posts.message, posts.id
                    FROM posts
                    JOIN users ON posts.user_id = users.id
                    WHERE posts.message ~* %s;
                """
                cur.execute(query, (pattern,))
                return cur.fetchall()
