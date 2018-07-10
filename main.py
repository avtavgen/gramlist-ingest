from skafossdk import *
from social.entity import SocialStatements
from gramlist.gramlist_proccessor import GramlistProcessor
from helpers.logger import get_logger


# Initialize the skafos  sdk
ska = Skafos()

ingest_log = get_logger('gramlist-fetch')

if __name__ == "__main__":
    ingest_log.info('Starting job')

    ingest_log.info('Fetching gramlist user data')
    entity = SocialStatements(ingest_log, ska.engine) # , ska.engine
    processor = GramlistProcessor(entity, ingest_log).fetch()
