import urllib.request
import json

class RedditImageSearchModule:
    """Inline пошук фотографій з NSFW контентом через Reddit"""

    async def client_ready(self, client, db):
        self.client = client

    async def piccmd(self, message):
        """Використання: .pic <пошуковий запит>"""
        query = message.text.split(maxsplit=1)[1]
        if not query:
            await message.answer("Введи пошуковий запит")
            return

        url = f"https://www.reddit.com/search.json?q={query}&include_over_18=on&sort=relevance"
        headers = {"User-Agent": "Mozilla/5.0"}

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())

            if "data" not in data or not data["data"]["children"]:
                await message.answer("Фотографій не знайдено")
                return

            results = []
            for item in data["data"]["children"][:10]:  # обмежуємо до 10 результатів
                post = item["data"]
                if "url_overridden_by_dest" in post and post["url_overridden_by_dest"].endswith(('.jpg', '.png', '.gif')):
                    results.append(
                        await self.client.inline_result(
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

            await self.client.inline_query(message.peer_id, results)
        except Exception as e:
            await message.answer(f"Сталася помилка: {e}")

    async def watcher(self, message):
        pass  # Необхідно, щоб модуль підтримував inline режим
