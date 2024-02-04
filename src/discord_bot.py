# pylint: disable=missing-module-docstring
import os
import time

from discord_webhook import DiscordWebhook, DiscordEmbed


class DiscordBot:
    """A class to interact with the Discord bot"""

    def __init__(self):
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.webhook = DiscordWebhook(url=webhook_url)

    def post_message(self, title, description, img_url, movie_id):
        """Post a message in the channel with the webhook """
        self.webhook.rate_limit_retry = True

        embed = DiscordEmbed(
            title=title,
            color="32a852",
            timestamp=int(time.time()),
            fields=[
                {
                    "name": "Theaters",
                    "value": description,
                    "inline": False,
                }
            ],
            url=f"https://www.ugc.fr/film.html?id={movie_id}",
            author={
                "name": "UGC Bot",
                "icon_url": "https://ugcdistribution.fr/wp-content/themes/bbxdesert/images/logo-ugc.png",
                "url": "https://www.ugc.fr",
            },
        )
        embed.set_image(url=img_url)
        self.webhook.add_embed(embed)

        self.webhook.execute(remove_embeds=True)
