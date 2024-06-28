from hikka.modules import Module, loader, utils
import urllib.request
import json

@loader.tds
class RedditImageSearchModule(Module):
    """Inline пошук фотографій з NSFW контентом через Reddit"""
    strings = {"name": "RedditImageSearch"}

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    async def piccmd(self, message):
        """Використання: .pic <пошуковий запит>"""
        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, "Введи пошуковий запит")
            return

        url = f"https://www.reddit.com/search.json?q={query}&include_over_18=on&sort=relevance"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())

            if "data" not in data or not data["data"]["children"]:
                await utils.answer(message, "Фотографій не знайдено")
                return

            results = []
            for item in data["data"]["children"][:10]:  # обмежуємо до 10 результатів
                post = item["data"]
                if "url_overridden_by_dest" in post and post["url_overridden_by_dest"].endswith(('.jpg', '.png', '.gif')):
                    results.append(
                        self.client.inline.result(
                            type='photo',
                            id=post["id"],
                            photo_url=post["url_overridden_by_dest"],
                            thumb_url=post["thumbnail"] if post["thumbnail"].startswith("http") else post["url_overridden_by_dest"],
                            photo_width=post["thumbnail_width"] if "thumbnail_width" in post else 100,
                            photo_height=post["thumbnail_height"] if "thumbnail_height" in post else 100,
                            title=post["title"] or "Фото",
                            description=f"З Subreddit: {post['subreddit']}"
                        )
                    )

            await self.client.inline.form(message=message, results=results)
        except Exception as e:
            await utils.answer(message, f"Сталася помилка: {e}")

    @loader.unrestricted
    async def watcher(self, message):
        pass  # Необхідно, щоб модуль підтримував inline режим
