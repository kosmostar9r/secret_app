import base64
import secrets
from typing import Annotated

from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.secret import GenerateInModel, SecretModel
from ..util.postgres import postgres_session_dependency

router = APIRouter()


@router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
    description="""
        Генерация ключа, по которому можно получить секрет с помощью кодовой фразы.
        """,
)
async def generate(
    request: Request,
    secret_model: GenerateInModel,
    db: AsyncSession = Depends(postgres_session_dependency),
) -> dict[str, str]:
    secret_key = secrets.token_urlsafe(32)
    key_hash = get_hash(secret_key, secret_model.secret_phrase)
    secret_data = Fernet(key_hash).encrypt(secret_model.secret.encode())
    secret_value = SecretModel(
        secret=secret_data,
        secret_key_hash=key_hash,
    )
    db.add(secret_value)
    await db.commit()
    await db.refresh(secret_value)
    return {"key": secret_key}


@router.get(
    "/secret/{secret_key}",
    description="""
        Получение секрета по ключу и фразе
        """,
)
async def get_secret(
    request: Request,
    secret_key: Annotated[
        str,
        Path(pattern=r"[\w\s]"),
    ],
    secret_phrase: Annotated[
        str,
        Query(min_length=2, max_length=20, pattern=r"[\w\s]"),
    ],
    db: AsyncSession = Depends(postgres_session_dependency),
) -> dict[str, str]:
    key_hash = get_hash(secret_key, secret_phrase)
    result = (
        (
            await db.execute(
                select(SecretModel.secret).where(
                    SecretModel.secret_key_hash == key_hash
                )
            )
        )
        .scalars()
        .one_or_none()
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="secret-key not found or expired",
        )
    await db.execute(delete(SecretModel).where(SecretModel.secret_key_hash == key_hash))
    await db.commit()
    return {"secret": Fernet(key_hash).decrypt(result).decode()}


def get_hash(key: str, phrase: str) -> bytes:
    return base64.urlsafe_b64encode(key.encode()[: 32 - len(phrase)] + phrase.encode())
