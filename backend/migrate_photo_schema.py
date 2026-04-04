import os

from sqlalchemy import create_engine, text


def main() -> None:
    database_url = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://photouser:photopass@localhost:3306/photowebapp",
    )
    engine = create_engine(database_url)

    with engine.begin() as connection:
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


if __name__ == "__main__":
    main()
