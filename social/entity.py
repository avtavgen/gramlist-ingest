import helpers


def batches(iterable, n=10):
    """divide a single list into a list of lists of size n """
    batchLen = len(iterable)
    for ndx in range(0, batchLen, n):
        yield list(iterable[ndx:min(ndx + n, batchLen)])


class SocialStatements:

    def __init__(self, logger, engine=None):
        self.users = []
        self.engine = engine
        self.logger = logger
        self.relations = []

    user_schema = {
        "table_name": "user",
        "options": {
            "primary_key": ["uri", "date"],
            "order_by": ["date desc"]
        },
        "columns": {
            "uri": "text",
            "screen_name": "text",
            "full_name": "text",
            "is_private": "boolean",
            "is_verified": "boolean",
            "profile": "text",
            "following": "int",
            "followers": "int",
            "categories": "set<text>",
            "url": "text",
            "lang": "text",
            "location": "text",
            "post_count": "int",
            "platform_income": "bigint",
            "date": "date",
            "last_fetch_id": "text",
            "ingested": "boolean",
            "engagement_rate": "text",
            "wow_growth": "text",
            "posting_average": "text",
            "likes_to_comments": "text"
        }
    }

    def save(self, batch_size=10, users=None):
        """Write these social statements to the data engine in the appropriate manner."""
        self.users = users
        if self.users:
            self.logger.info('about to send {} user statements to the data engine'.format(len(self.users)))
            self._write_batches(self.engine, self.logger, self.user_schema, self.users, batch_size)
        else:
            self.logger.debug('skipping user ingest, no records in these social statements')

    @staticmethod
    def _write_batches(engine, logger, schema, data, batch_size=40):
        for rows in batches(data, batch_size):
            logger.info('Rows: {}'.format(rows))
            res = engine.save(schema, list(rows)).result()
            logger.info(res)
