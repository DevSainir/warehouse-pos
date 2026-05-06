import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password


async def create_admin():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            User.__table__.select().where(User.name == "admin")
        )
        exists = result.first()

        if exists:
            print("Admin already exists")
            return

        admin = User(
            name="admin",
            password_hash=hash_password("12341234"),
            role=UserRole.admin,
            is_active=True,
        )

        session.add(admin)
        await session.commit()
        print("Admin created successfully")


if __name__ == "__main__":
    asyncio.run(create_admin())
