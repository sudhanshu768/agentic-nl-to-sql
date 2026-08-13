from app.metadata.loader import (
    format_schema_for_llm,
    load_schema_metadata,
)


def main() -> None:
    metadata = load_schema_metadata()

    print("Schema metadata loaded successfully.")
    print()

    print(
        "Database:",
        metadata["database"],
    )

    print(
        "Dialect:",
        metadata["dialect"],
    )

    print(
        "Tables:",
        len(metadata["tables"]),
    )

    print()

    formatted_schema = format_schema_for_llm(
        metadata
    )

    print(formatted_schema)


if __name__ == "__main__":
    main()