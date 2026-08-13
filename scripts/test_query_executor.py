from app.database.executor import QueryExecutor


def main() -> None:

    executor = QueryExecutor()

    sql = """
    SELECT
        c.name,
        SUM(o.total_amount) AS total_spending
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    WHERE o.status <> 'cancelled'
    GROUP BY c.customer_id, c.name
    ORDER BY total_spending DESC
    LIMIT 5;
    """

    result = executor.execute(sql)

    print("Columns:")
    print(result.columns)

    print()
    print("Rows:")

    for row in result.rows:
        print(row)

    print()
    print(
        "Rows returned:",
        result.row_count,
    )


if __name__ == "__main__":
    main()