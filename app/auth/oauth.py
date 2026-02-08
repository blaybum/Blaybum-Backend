from typing import Any, Dict, Optional, Tuple, cast

from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import BaseOAuth2
import httpx

from app.settings import settings


class CustomGoogleOAuth2(GoogleOAuth2):
    """Custom Google OAuth2 client that uses UserInfo API instead of People API"""
    
    async def get_id_email(self, token: str) -> Tuple[str, Optional[str]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            data = response.json()
            
            user_id = data["id"]
            email = data.get("email")
            return user_id, email


google_oauth_client = CustomGoogleOAuth2(
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
)


class KakaoOAuth2(BaseOAuth2[Dict[str, Any]]):

    display_name = "Kakao"
    logo_svg = ""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: Optional[list[str]] = None,
        name: str = "kakao",
    ):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            authorize_endpoint="https://kauth.kakao.com/oauth/authorize",
            access_token_endpoint="https://kauth.kakao.com/oauth/token",
            refresh_token_endpoint="https://kauth.kakao.com/oauth/token",
            revoke_token_endpoint="https://kapi.kakao.com/v1/user/unlink",
            revocation_endpoint_auth_method="client_secret_post",
            base_scopes=scopes or ["profile_nickname", "profile_image", "account_email"],
            name=name,
        )

    async def get_id_email(self, token: str) -> Tuple[str, Optional[str]]:

        async with self.get_httpx_client() as client:
            response = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            data = response.json()

            user_id = str(data["id"])
            kakao_account = data.get("kakao_account", {})
            email = kakao_account.get("email")

            return user_id, email

    async def get_profile_info(self, token: str) -> Dict[str, Any]:

        async with self.get_httpx_client() as client:
            response = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            data = response.json()

            kakao_account = data.get("kakao_account", {})
            profile = kakao_account.get("profile", {})

            return {
                "id": str(data["id"]),
                "email": kakao_account.get("email"),
                "nickname": profile.get("nickname"),
                "profile_image": profile.get("profile_image_url"),
            }

kakao_oauth_client = KakaoOAuth2(
    client_id=settings.kakao_client_id,
    client_secret=settings.kakao_client_secret,
)
