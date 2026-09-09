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
        return [{"id":comment["id"], "comment":comment['text'], "createdAt":comment["created_at"]} for comment in data.get('children', []) if 'text' in comment]
    else:
        print(f"Error fetching comments for thread {thread_id}: {response.status_code}")
        return []

def save_comments_to_db(thread, comments):
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
            updated_comment = update_a_tag(comment["comment"])
            if updated_comment == "error":
                print(f"Error processing comment {comment['id']}. Skipping...")
                continue
            soup = BeautifulSoup(updated_comment, "html.parser")
            try:
                cursor.execute(
                    "INSERT INTO posting "
                    "(source, source_id, raw_html, text, posted_at, thread_month, fetched_at ) "
                    "VALUES ('hn', %s, %s, %s, %s, %s, NOW())",
                    (comment["id"], comment["comment"],soup.get_text(separator=HTML_SEPARATOR),comment["createdAt"],thread["thread_month"] )
                )
                connection.commit()

            except UniqueViolation as e:
                print(f"Duplicate entry for comment {comment['id']}: {e}")
                connection.rollback()
                cursor.execute(
                    "UPDATE posting SET " 
                    "raw_html = %s, text = %s, fetched_at = NOW() WHERE source='hn' AND source_id=%s ;",
                    (comment["comment"],soup.get_text(separator=HTML_SEPARATOR),str(comment["id"])))
                connection.commit()

        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error saving comments to the database: {e}")
    print(f"Saving comments for thread {thread['id']} to the database...")


def main():
    threads = get_hiring_threads()
    for thread in threads:
        comments = get_thread_comments(thread["id"])
        save_comments_to_db(thread, comments)

def update_a_tag(comment):
    try:
        soup = BeautifulSoup(comment, 'html.parser')
        for a_tag in soup.find_all('a'):
            if a_tag and a_tag.has_attr('href') and a_tag.string != a_tag['href']:
                a_tag.string = a_tag['href']
    except Exception as e:
        return "error"
    return str(soup)

if __name__ == "__main__":
    main()

