from app.agents.sql_generator import SQLGenerator
from app.llm.gemini_provider import GeminiProvider


def main() -> None:

    llm = GeminiProvider()

    generator = SQLGenerator(
        llm=llm
    )

    question = (
        "Show the top 5 customers "
        "by total spending."
    )

    print("Question:")
    print(question)

    print()
    print("Generated SQL:")
    print()

    sql = generator.generate_sql(
        question
    )

    print(sql)


if __name__ == "__main__":
    main()