import argparse
import logging
from populate_vectorstore import load_documents, clear_database, add_to_json_vectors
logger = logging.getLogger(__name__)

def main():

    logging.basicConfig(filename='vector_log.log', level=logging.INFO)
    logger.info('DB Population Started')
    print("========== RUNNING SET UP FILE ============")
    
    # Check if the database should be cleared (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the json vector store.")
    parser.add_argument("--populate", action="store_true", help="populate json vector store.")
    args = parser.parse_args()

    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    print(f"------- Terminal args: {args} ------")

    if args.populate:
        # Create (or update) the data store.
        documents = load_documents()

        # chunks = split_documents(documents)
        add_to_json_vectors(documents)

if __name__ == "__main__":
    main()