import os
import time

from sqlalchemy import create_engine, text


def reconcile_photo_schema(engine) -> None:
    with engine.begin() as connection:
        table_exists = connection.execute(text("SHOW TABLES LIKE 'photos'")).first()
        if not table_exists:
            return

        rows = list(connection.execute(text("SHOW COLUMNS FROM photos")))
        columns = {row[0] for row in rows}

        if "content_type" not in columns:
            connection.execute(
                text("ALTER TABLE photos ADD COLUMN content_type VARCHAR(100) NULL")
            )

        if "image_data" not in columns:
            connection.execute(
                text("ALTER TABLE photos ADD COLUMN image_data LONGBLOB NULL")
            )
        else:
            image_data_row = next((row for row in rows if row[0] == "image_data"), None)
            image_data_type = (image_data_row[1].lower() if image_data_row and len(image_data_row) > 1 else "")
            if image_data_type != "longblob":
                connection.execute(
                    text("ALTER TABLE photos MODIFY COLUMN image_data LONGBLOB NULL")
                )


def main() -> None:
    database_url = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://photouser:photopass@localhost:3306/photowebapp",
    )
    engine = create_engine(database_url)

    last_error = None
    for _ in range(30):
        try:
            reconcile_photo_schema(engine)
            return
        except Exception as exc:
            last_error = exc
            time.sleep(2)

    raise RuntimeError(f"Schema migration failed: {last_error}")


if __name__ == "__main__":
    main()
