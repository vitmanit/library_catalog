from domain.BaseApi import BaseApiClient
import httpx


def extract_description(desc):
    # desc может быть str или dict {"type": "...", "value": "..."}
    if isinstance(desc, str):
        return desc
    if isinstance(desc, dict):
        return desc.get("value") or desc.get("description") or ""
    return ""

class SearchInfo(BaseApiClient):
    def __init__(self, title: str):
        self.title = title

    async def get(self):
        params = {
            "title": self.title,
            "limit": 1,
            "fields": ",".join([
                "key",
                "ratings_average", "ratings_count",
                "editions", "editions.key", "editions.isbn", "editions.publish_date"
            ]),
        }
        self.log_info(f'Получил title {self.title} приступаю к поиску')
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                # Первый запрос
                r = await client.get("https://openlibrary.org/search.json", params=params)
                self.log_info(f'Параметры запроса = {params}')
                r.raise_for_status()
                work = r.json()["docs"][0]

                # ключ работы
                key = work.get("key")
                self.log_info(f'Получил ключ книги для поиска = {key}')

                # ISBN
                ed = (work.get("editions", {}).get("docs") or [None])[0] or {}
                isbns = ed.get("isbn", [])
                self.log_info(f'Получили isbn = {isbns}')

                # Обложка
                cover_url = f"https://covers.openlibrary.org/b/isbn/{isbns[0]}-M.jpg" if isbns else None
                self.log_info(f'Получили ссылку на обложку = {cover_url}')

                # Второй запрос (описание)
                resp = await client.get(f"https://openlibrary.org{key}.json")
                resp.raise_for_status()
                raw_desc = resp.json().get("description")
                description = extract_description(raw_desc)
                self.log_info(f'Описание = {description}')

                # рейтинг
                rating = work.get("ratings_average")
                self.log_info(f'Рейтинг = {rating}')
        except Exception as e:
            self.log_error(f'Получили ошибку: {e}')
            raise

        return description, rating, cover_url

    async def post(self):
        pass