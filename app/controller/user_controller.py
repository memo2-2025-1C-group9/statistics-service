from app.services.user_service import (
    validate_user,
)


async def handle_validate_user(token: str):
    return await validate_user(token)
