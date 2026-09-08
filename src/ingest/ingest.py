import requests
import psycopg2
from bs4 import BeautifulSoup

def get_hiring_threads():
    threadIds = []
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
        return [hits['objectID'] for hits in data['hits']]
    else:
        print(f"Error fetching hiring threads: {response.status_code}")
        return []

def get_thread_comments(thread_id):
    base_url = f"https://hn.algolia.com/api/v1/items/{thread_id}"
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        return [{"id":comment["id"], "comment":comment['text'], "createdAt":comment["created_at"],"thread_month":comment["created_at"][5:7]} for comment in data.get('children', []) if 'text' in comment]
    else:
        print(f"Error fetching comments for thread {thread_id}: {response.status_code}")
        return []

def save_comments_to_db(thread_id, comments):
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
        for comment in comments:
            print(comment)
            soup = BeautifulSoup(comment["comment"], 'html.parser')
            cursor.execute(
                "INSERT INTO posting "
                "(source, source_id, raw_html, text, posted_at, thread_month, fetched_at ) "
                "VALUES ('hn', %s, %s, %s, %s, %s, NOW())",
                (comment["id"], comment["comment"],soup.get_text(),comment["createdAt"],comment["thread_month"] )
            )
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error saving comments to the database: {e}")
    print(f"Saving comments for thread {thread_id} to the database...")


def main():
    thread_ids = get_hiring_threads()
    for thread_id in thread_ids:
        comments = get_thread_comments(thread_id)
        save_comments_to_db(thread_id, comments)

if __name__ == "__main__":
    main()

