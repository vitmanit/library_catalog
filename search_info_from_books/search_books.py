from HTTP_REQUEST.BaseApi import BaseApiClient
import httpx
import asyncio

def extract_description(desc):
    # desc может быть str или dict {"type": "...", "value": "..."}
    if isinstance(desc, str):
        return desc
    if isinstance(desc, dict):
        return desc.get("value") or desc.get("description") or ""
    return ""

class SearchInfo(BaseApiClient):
    @staticmethod
    async def get(title: str):
        params = {
            "title": title,
            "limit": 1,
            "fields": ",".join([
                "key",
                "ratings_average", "ratings_count",
                "editions", "editions.key", "editions.isbn", "editions.publish_date"
            ]),
        }
        async with httpx.AsyncClient(timeout=20) as client:
            # Первый запрос
            r = await client.get("https://openlibrary.org/search.json", params=params)
            r.raise_for_status()
            work = r.json()["docs"][0]

            # ключ работы
            key = work.get("key")

            # ISBN
            ed = (work.get("editions", {}).get("docs") or [None])[0] or {}
            isbns = ed.get("isbn", [])

            # Обложка
            cover_url = f"https://covers.openlibrary.org/b/isbn/{isbns[0]}-M.jpg" if isbns else None

            # Второй запрос (описание)
            resp = await client.get(f"https://openlibrary.org{key}.json")
            resp.raise_for_status()
            raw_desc = resp.json().get("description")
            description = extract_description(raw_desc)

            # рейтинг
            rating = work.get("ratings_average")

        return description, rating, cover_url


res = asyncio.run(SearchInfo.get('The Adventures of Sherlock Holmes'))
print(res)