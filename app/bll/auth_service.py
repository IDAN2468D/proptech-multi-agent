from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AuthenticationError, PropTechBaseException
from app.core.security import create_access_token, hash_password, verify_password
from app.dal.mongo.memory_repository import InvestorMemoryRepository
from app.dal.sql.repositories import UserRepository
from app.models.auth_schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)


class AuthService:
    """Business Logic Layer service for user registration and JWT authentication."""

    def __init__(self, session: AsyncSession) -> None:
        self.user_repo = UserRepository(session)
        self.memory_repo = InvestorMemoryRepository()

    async def register_user(self, payload: UserRegisterRequest) -> UserResponse:
        existing = await self.user_repo.get_by_email(payload.email)
        if existing:
            raise PropTechBaseException(
                message=f"User with email '{payload.email}' is already registered.",
                error_code="USER_ALREADY_EXISTS",
                status_code=409,
            )
        hashed = hash_password(payload.password)
        user = await self.user_repo.create(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hashed,
        )
        # Initialize default Long-Term Investor Memory in MongoDB
        await self.memory_repo.get_investor_profile(user.id)
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
        )

    async def authenticate_user(self, payload: UserLoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        token = create_access_token(subject=user.id, email=user.email)
        return TokenResponse(
            access_token=token,
            user_id=user.id,
            email=user.email,
        )
