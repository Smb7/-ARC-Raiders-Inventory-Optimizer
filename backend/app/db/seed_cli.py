from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.seed import seed_static_data
from app.db.session import to_sync_database_url


def main() -> None:
    engine = create_engine(to_sync_database_url(settings.database_url))
    with Session(engine) as session:
        seed_static_data(session)


if __name__ == "__main__":
    main()
