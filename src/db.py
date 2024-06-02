import psycopg

dbname = "test"
user = "postgres"


def test():
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
                print(record)


def connect():
    return psycopg.connect("dbname={} user={}".format(dbname, user))


test()
