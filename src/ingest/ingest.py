import argparse
import json
import sys

import requests
import psycopg2
from bs4 import BeautifulSoup
from psycopg2.errors import UniqueViolation

HTML_SEPARATOR = "\n"
def get_hiring_threads():

    base_url = "https://hn.algolia.com/api/v1/search_by_date?query=Ask%20HN:%20Who%20is%20hiring?&tags=story,author_whoishiring"
    params = {
        "hitsPerPage": 1,
        "page": 0,
        "query": "Ask HN: Who is hiring?",
        "tags": "story,author_whoishiring",
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [{"id": hits['objectID'], "thread_month":hits["created_at"][0:4]+"-"+hits["created_at"][5:7]} for hits in data['hits']]
    else:
        print(f"Error fetching hiring threads: {response.status_code}")
        return []

def get_thread_comments(thread_id):
    base_url = f"https://hn.algolia.com/api/v1/items/{thread_id}"
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching comments for thread {thread_id}: {response.status_code}")
        return {}

def save_comments_to_cache(thread, comments):
    connection = psycopg2.connect(
        dbname="project_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO posting_cache "
            "(thread_id, source, postings,thread_month,fetched_at ) "
            "VALUES (%s,'hn', %s,%s,  NOW())",
            (thread["id"], json.dumps(comments), thread['thread_month'] )
        )
        connection.commit()
        cursor.close()
        connection.close()
    except UniqueViolation:
        print(f"Duplicate entry for thread {thread['id']}. Updating existing entry.")
        connection.rollback()
        cursor.execute(
            "UPDATE posting_cache SET " 
            "postings = %s, fetched_at = NOW() WHERE thread_id=%s ;",
            (json.dumps(comments), thread["id"] ))
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error saving comments to the cache: {e}")


def store_threads() :
    threads = get_hiring_threads()
    for thread in threads:
        comments = get_thread_comments(thread["id"])
        save_comments_to_cache(thread, comments)

def save_comments_to_db(thread):
    # Placeholder function to save comments to a database
    # Implement your database saving logic here
    try:
        connection = psycopg2.connect(
            dbname="project_db",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        comments = thread["comments"].get('children', [])
        for comment in comments:
            updated_comment = None if comment.get("text") is None  else update_a_tag(comment["text"])
            if updated_comment is None:
                continue
            soup = BeautifulSoup(updated_comment, "html.parser")
            try:
                cursor.execute(
                    "INSERT INTO posting "
                    "(source, source_id, raw_html, text, posted_at, thread_month, fetched_at ) "
                    "VALUES ('hn', %s, %s, %s, %s, %s, NOW())",
                    (comment["id"], comment["text"],soup.get_text(separator=HTML_SEPARATOR),comment["created_at"],thread["thread_month"] )
                )
                connection.commit()

            except UniqueViolation as e:
                print(f"Duplicate entry for comment {comment['id']}: {e}")
                connection.rollback()
                cursor.execute(
                    "UPDATE posting SET " 
                    "raw_html = %s, text = %s, fetched_at = NOW() WHERE source='hn' AND source_id=%s ;",
                    (comment["text"],soup.get_text(separator=HTML_SEPARATOR),str(comment["id"])))
                connection.commit()

        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error saving comments to the database: {e}")


def update_a_tag(comment):
    try:
        soup = BeautifulSoup(comment, 'html.parser')
        for a_tag in soup.find_all('a'):
            if a_tag and a_tag.has_attr('href') and a_tag.string != a_tag['href']:
                a_tag.string = a_tag['href']
    except Exception as e :
        print(f"Error processing comment: {comment} with error -{e}")
        return None
    return str(soup)

def get_threads_from_cache():
    connection = psycopg2.connect(
        dbname="project_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT thread_id, postings, thread_month FROM posting_cache")
        threads = cursor.fetchall()
        cursor.close()
        connection.close()
        return [{"id": thread[0], "comments": thread[1], "thread_month":thread[2]} for thread in threads]
    except Exception as e:
        print(f"Error fetching threads from the database: {e}")
        return []


def main(argv=None):
    # 1. Setup the parser
    parser = argparse.ArgumentParser(description="Script running inside main.")
    parser.add_argument("--refresh", action="store_true", help="Trigger a data refresh")

    # 2. Parse the arguments.
    # Passing 'argv' here tells argparse to read the list we handed to main()
    args = parser.parse_args(argv)

    # 3. Your logic
    if args.refresh:
        store_threads()
    threads = get_threads_from_cache()
    for thread in threads:
        save_comments_to_db(thread)

if __name__ == "__main__":
    main(sys.argv[1:])

