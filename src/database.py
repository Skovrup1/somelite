import psycopg
from enum import IntEnum, auto
from werkzeug.security import generate_password_hash
from faker import Faker
import random

fake = Faker()


class Relation(IntEnum):
    friends = auto()


class Db:
    def __init__(
        self,
        name,
        user=None,
        password=None,
        admin_user="postgres",
        admin_password=None,
    ):
        self.name = name

        if user:
            self.user = user
        else:
            self.user = name

        if password:
            self.password = password
        else:
            self.password = name

        self.admin_user = admin_user

        if admin_password:
            self.admin_password = admin_password
        else:
            self.admin_password = admin_user

    def delete(self):
        with psycopg.connect(
            "dbname={} user={} password={}".format(
                self.admin_user, self.admin_user, self.admin_password
            )
        ) as conn:
            conn.autocommit = True

            with conn.cursor() as cur:
                try:
                    cur.execute("DROP DATABASE {}".format(self.name))
                except psycopg.ProgrammingError:
                    pass

                try:
                    cur.execute("DROP USER {}".format(self.user))
                except psycopg.ProgrammingError:
                    pass

    def create(self):
        with psycopg.connect(
            "dbname={} user={} password={}".format(
                self.admin_user, self.admin_user, self.admin_password
            )
        ) as conn:
            conn.autocommit = True

            with conn.cursor() as cur:
                cur.execute(
                    "CREATE USER {} WITH PASSWORD '{}'".format(self.user, self.password)
                )

                cur.execute("CREATE DATABASE {} OWNER {}".format(self.name, self.user))

    def connect(self):
        conn = psycopg.connect(
            "dbname={} user={} password={}".format(self.name, self.user, self.password)
        )
        conn.autocommit = True

        return conn

    def create_tables(self):
        with self.connect() as conn:
            conn.autocommit = True

            with conn.cursor() as cur:
                cur.execute("""CREATE TABLE users (
                                id serial PRIMARY KEY,
                                name text,
                                email text,
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
                                date TIMESTAMP,
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

                self.insert_placeholder_data(cur, 20)

    def create_user(cur, name, email, password, age):
        hash_pass = generate_password_hash(password)

        cur.execute(
            "INSERT INTO users (name, email, password, age) VALUES (%s, %s, %s, %s)",
            (name, email, hash_pass, age),
        )

    def add_post(cur, id, date="CURRENT_TIMESTAMP", message=""):
        cur.execute(
            "INSERT INTO posts (user_id, date, message) VALUES ('{}', {}, '{}')".format(
                id, date, message
            )
        )

    def delete_post(cur, post_id):
        cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))

    def get_user(cur, id):
        cur.execute(
            """
                    SELECT *
                    FROM users
                    WHERE id = %s
                    """,
            (id,),
        )

        return cur.fetchone()

    def get_user_by_email(cur, email):
        print("GETUSER")
        print(email)
        cur.execute(
            """
                    SELECT *
                    FROM users
                    WHERE email = %s
                    """,
            (email,),
        )

        return cur.fetchone()

    def delete_user(self, curx, idx):
        curx.execute("DELETE FROM users WHERE id = %s", (idx,))

    def get_users(cur):
        cur.execute("SELECT * FROM users")

        return cur.fetchall()

    def get_posts(self):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            SELECT *
                            FROM posts
                            """)

                return cur.fetchall()

    def get_names_and_posts(cur):
        cur.execute("""
                    SELECT users.name, posts.id, posts.user_id, posts.date, posts.message
                    FROM users
                    JOIN posts ON users.id = posts.user_id;
                    """)
        return cur.fetchall()

    def get_posts_of_friends(self, id):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT users.name, posts.id, posts.user_id, posts.date, posts.message
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

    def insert_placeholder_data(self, cur, n):
        Db.create_user(cur, "alice", "alice@alice", "alice", 30)
        Db.create_user(cur, "bob", "bob@bob", "bob", 35)
        Db.create_user(cur, "charlie", "charlie@charlie", "charlie", 25)
        Db.create_user(cur, "david", "david@David", "david", 40)

        # Generate random users
        for _ in range(5, n + 1):
            first_name = fake.first_name()
            name = first_name
            email = fake.email()
            password = name  # fake.password()
            age = random.randint(18, 80)
            Db.create_user(cur, name, email, password, age)

        # Inserting data into the 'groups' table
        cur.execute("INSERT INTO groups (user_id, name) VALUES (%s, %s)", (1, "Staff"))
        cur.execute(
            "INSERT INTO groups (user_id, name) VALUES (%s, %s)", (2, "Student")
        )
        cur.execute("INSERT INTO groups (user_id, name) VALUES (%s, %s)", (3, "Alumni"))

        # Inserting data into the 'posts' table
        Db.add_post(cur, 1, message="Hello, world!")
        Db.add_post(cur, 2, message="This is a test post.")
        Db.add_post(cur, 3, message="Welcome to my domain!")
        Db.add_post(cur, 4, message="Test post, please ignore")

        # Generate random texts
        for i in range(5, n + 1):
            post_message = fake.text()  # Generate a random text message
            Db.add_post(cur, i, message=post_message)

        # Adding a relationship
        self.add_relation(1, 2, Relation.friends)
        self.add_relation(1, 3, Relation.friends)

        # Creating Groups
        Db.add_group(cur, 2, "Bob og Charlie's gruppe")

        # Adding Group Memberships
        Db.join_group(cur, 1, 1)
        Db.join_group(cur, 2, 1)
        Db.join_group(cur, 2, 4)
        Db.join_group(cur, 3, 4)

        # # Removing a relationship
        # remove_relation(1, 2)
        # remove_relation(1,3)

        # Adding some likes
        self.like_post(1, 1)
        self.like_post(1, 1)
        self.like_post(1, 2)
        self.like_post(3, 1)
        self.like_post(2, 3)
        self.like_post(1, 4)

        # Testing show_all_likes function
        # print("Number of likes for post 1:", self.show_all_likes(1))
        # print("Number of likes for post 2:", self.show_all_likes(2))
        # print("Number of likes for post 3:", self.show_all_likes(3))
        # print("Number of likes for post 4:", self.show_all_likes(4))

        # Testing regular_match function
        # print("Posts matching 'world':", self.regular_match("world"))
        # print("Posts matching 'WORLD':", self.regular_match("WORLD"))
        # print("Posts matching 'hello world':", self.regular_match("hello world"))
        # print("Posts matching 'test world':", self.regular_match("test world"))

        print("Test : ", self.get_posts_of_groups_ordered(2))

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

    # Given a group id, returns all the posts made by its members
    def get_posts_of_group(self, groupid):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT users.name, posts.id, posts.user_id, posts.date, posts.message
                    FROM posts
                    JOIN users
                    ON posts.user_id = users.id
                    WHERE posts.user_id IN (
                        SELECT user_id
                        FROM group_memberships
                        WHERE group_id = %(groupid)s
                    );
                """,
                    {"groupid": groupid},
                )
                return cur.fetchall()

    # Given a user_id, returns all the posts made by people who share a group with that person
    def get_posts_of_groups(self, user_id):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT users.name, posts.id, posts.user_id, posts.date, posts.message
                    FROM posts
                    JOIN users
                    ON posts.user_id = users.id
                    WHERE posts.user_id IN (
                        SELECT user_id
                        FROM group_memberships
                        WHERE group_id IN(
                            SELECT group_id
                            FROM group_memberships
                            WHERE user_id = %(user_id)s
                        )
                    )
                    """,
                    {"user_id": user_id},
                )
                return cur.fetchall()

    # Given a group ID, returns the name of the corresponding group
    def get_name_of_group(self, group_id):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT name
                    FROM groups
                    WHERE id = %(group_id)s
                    """,
                    {"group_id": group_id},
                )
                return cur.fetchone()

    # Returns a list of the names of groups a given user is a member of, and the posts made by their members
    def get_posts_of_groups_ordered(self, user_id):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT group_id
                    FROM group_memberships
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                group_ids = cur.fetchall()

                result = []
                for id in group_ids:
                    posts = Db.get_posts_of_group(self, (id[0]))
                    name = Db.get_name_of_group(self, id[0])
                    result.append((posts, name[0]))

                return result
