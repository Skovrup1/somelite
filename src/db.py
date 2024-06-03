import psycopg

dbname = "somelite"
user = "postgres"

def connect():
    return psycopg.connect("dbname={} user={}".format(dbname, user))


def get_users():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM users")

            return cur.fetchall()


'''def test():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE test5 (
                    id serial PRIMARY KEY,
                    num integer,
                    data text)
                        """)

            cur.execute(
                "INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def")
            )

            cur.execute("SELECT * FROM test")
            cur.fetchone()

            for record in cur:
                print(record)'''
