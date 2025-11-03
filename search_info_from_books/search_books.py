import requests

def extract_description(desc):
    # desc может быть str или dict {"type": "...", "value": "..."}
    if isinstance(desc, str):
        return desc
    if isinstance(desc, dict):
        return desc.get("value") or desc.get("description") or ""
    return ""


class SearchInfo:
    @staticmethod
    def additional_info(title: str):
        params = {
            "title": title,
            "limit": 1,
            "fields": ",".join([
                "key",
                "ratings_average","ratings_count",
                "editions","editions.key","editions.isbn","editions.publish_date"
            ]),
        }
        r = requests.get("https://openlibrary.org/search.json", params=params, timeout=20)
        r.raise_for_status()
        work = r.json()["docs"][0]

        # ключ работы
        key = work.get("key")  # например: "/works/OL82548W" [web:47]

        # ISBN
        ed = (work.get("editions", {}).get("docs") or [None])[0] or {}
        isbns = ed.get("isbn", [])

        #Обложка
        cover_url = f"https://covers.openlibrary.org/b/isbn/{isbns[0]}-M.jpg"  # S/M/L [web:1]

        # описание работы (может быть str или объект)
        resp = requests.get(f"https://openlibrary.org{key}.json", timeout=20)
        resp.raise_for_status()
        raw_desc = resp.json().get("description")
        description = extract_description(raw_desc)

        # рейтинг с уровня работы (если доступен в выдаче поиска)
        rating = work.get("ratings_average")

        return description, rating, cover_url


    #Поиск всей инфы (на будущее)
    @staticmethod
    def search_with_isbn(title: str):
        params = {
            "title": title,
            "limit": 1,
            "fields": ",".join([
                "key", "title", "author_name", "first_publish_year",
                "ratings_average",
                "editions", "editions.key", "editions.isbn", "editions.publish_date"
            ]),
        }
        r = requests.get("https://openlibrary.org/search.json", params=params, timeout=20)
        r.raise_for_status()
        doc = r.json()["docs"][0]
        work = {
            "title": doc.get("title"),
            "authors": doc.get("author_name", []),
            "first_year": doc.get("first_publish_year"),
            "rating": doc.get("ratings_average"), "key": doc.get("key")
        }
        ed = (doc.get("editions", {}).get("docs") or [None])[0] or {}
        isbns = ed.get("isbn", [])
        publish_date = ed.get("publish_date")
        return work, isbns[0], publish_date