"""Lorem ipsum."""

from litestar import Controller, Request, post

DISCORD_AUTH_URL: str = "https://discord.com/oauth2/authorize"
DISCORD_TOKEN_URL: str = "https://discord.com/api/oauth2/token"  # noqa: S105 # not a password
DISCORD_TOKEN_REVOKE_URL: str = "https://discord.com/api/oauth2/token"  # noqa: S105 # not a password

SCOPES: set[str] = {"guilds", "identify", "applications.commands"}
WEBHOOK_SCOPES: set[str] = {"guilds", "idenify", "applications.commands", "webhook.incoming"}


class DiscordOAuth2Controller(Controller):
    """Lorem ipsum."""

    path = "/discord"

    @post("/callback")
    async def oauth2_callback(self, request: Request, state: str, code: str) -> None:
        """Lorem ipsum."""
