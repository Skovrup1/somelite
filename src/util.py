class Util:
    def convert_to_web(posts):
        new_posts = []
        for post in posts:
            new_posts.append(
                (post[0].capitalize(), post[1].strftime("%H.%M, %A %d, %B"), post[2])
            )

        return new_posts
