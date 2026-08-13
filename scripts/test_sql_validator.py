from app.security.sql_validator import SQLValidator


def test_query(
    validator: SQLValidator,
    sql: str,
) -> None:

    result = validator.validate(
        sql
    )

    print("-" * 60)
    print("SQL:")
    print(sql)

    print()
    print(
        "Valid:",
        result.is_valid,
    )

    if result.error:
        print(
            "Error:",
            result.error,
        )


def main() -> None:

    validator = SQLValidator()

    # Valid
    test_query(
        validator,
        """
SELECT
    c.name,
    SUM(o.total_amount) AS spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY spending DESC;
""",
    )

    # Unknown column
    test_query(
        validator,
        """
SELECT c.customer_name
FROM customers c;
""",
    )

    # Unknown table
    test_query(
        validator,
        """
SELECT *
FROM fake_table;
""",
    )

    # DELETE
    test_query(
        validator,
        """
DELETE FROM customers;
""",
    )

    # Multiple statements
    test_query(
        validator,
        """
SELECT *
FROM customers;

DROP TABLE customers;
""",
    )


if __name__ == "__main__":
    main()