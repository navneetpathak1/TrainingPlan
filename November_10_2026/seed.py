from database import SessionLocal, engine, Base
from models import User, Todos


def seed_database():

    # Create database tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        existing_user = db.query(User).filter(
            User.username == "navneet"
        ).first()

        if existing_user:
            print("Seed data already exists!")
            return

        # Create users
        user1 = User(
            username="navneet",
            password="password123"
        )

        user2 = User(
            username="rahul",
            password="password456"
        )

        db.add_all([user1, user2])
        db.flush()

        # Create todos
        todo1 = Todos(
            title="Learn FastAPI",
            content="Understand FastAPI CRUD operations",
            user_id=user1.id
        )

        todo2 = Todos(
            title="Learn SQLAlchemy",
            content="Understand SQLAlchemy ORM",
            user_id=user1.id
        )

        todo3 = Todos(
            title="Practice Python",
            content="Practice Python functions",
            user_id=user2.id
        )

        db.add_all([todo1, todo2, todo3])

        db.commit()

        print("Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()