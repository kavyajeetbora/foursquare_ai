"""
LangChain pipeline setup and utilities.
"""
# Example placeholder for LangChain integration
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser
from src.bot.models import FourSquareChatBot

from dotenv import load_dotenv
load_dotenv(dotenv_path = ".env", override=True)

def initiate_chat_bot():
    SYSTEM_MESSAGE = """
    Given an input question, create a syntactically correct DuckDB SQL query to answer it using data from Parquet files at {data_path}.
    Limit results to {top_k} unless the user specifies a different number, ordering by a relevant column for the most interesting results.
    Use only columns: `name`, `category`, `address`, `region`, `postcode`.
    For keyword searches (e.g., "temple," "hotel"),
    search across `name`, `category`, and `address` using LOWER() and LIKE, prioritizing matches in `category` via ORDER BY CASE.
    For region-specific queries, check `region` and `address` columns.

    Restrict outlets (POIs) to India only.
    If a non-India country is mentioned, respond with "Query beyond scope, restricted to India" and do not generate a query.

    Use read_parquet('{data_path}') as the data source.

    Schema: {table_info}
    User question: {input}
    Limit: {top_k}
    Output only the Duckdb query without explanations.
    Strictly stick to the above mentioned schema only.

    Few Shot Examples:
    - Question: How many temples are there in India?
    - Query: SELECT COUNT(*) as count FROM read_parquet('{data_path}') WHERE LOWER(name) LIKE '%temple%' OR LOWER(category) LIKE '%temple%' LIMIT {top_k};

    - Question: Which hotels are located in Goa?
    - Query: SELECT name, category_level_1, category_level_2, address, region, postcode FROM read_parquet('{data_path}') WHERE (LOWER(name) LIKE '%hotel%' OR LOWER(category) LIKE '%hotel%') AND (LOWER(region) LIKE '%goa%' OR LOWER(address) LIKE '%goa%') LIMIT {top_k};

    - Question: List petrol pumps in Chennai.
    - Query: SELECT name, category_level_1, category_level_2, address, region, postcode FROM read_parquet('{data_path}') WHERE LOWER(category) LIKE '%petrol%' AND (LOWER(region) LIKE '%chennai%' OR LOWER(address) LIKE '%chennai%') LIMIT {top_k};

    - Question: How many restaurants are in Bangalore?
    - Query: SELECT COUNT(*) as count FROM read_parquet('{data_path}') WHERE LOWER(category) LIKE '%restaurant%' AND (LOWER(region) LIKE '%bangalore%' OR LOWER(address) LIKE '%bangalore%') LIMIT {top_k};

    - Question: Find bookstores in Delhi.
    - Query: SELECT name, category_level_1, category_level_2, address, region, postcode FROM read_parquet('{data_path}') WHERE LOWER(category) LIKE '%bookstore%' AND (LOWER(region) LIKE '%delhi%' OR LOWER(address) LIKE '%delhi%') LIMIT {top_k};
    """
    user_prompt = "Question: {input}"
    query_prompt_template = ChatPromptTemplate.from_messages([("system", SYSTEM_MESSAGE), ("user", user_prompt)])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    fsq_chat_bot = FourSquareChatBot(
        data_path = "data\output.geoparquet",
        columns = ['name', 'category', 'address', 'region', 'postcode'],
        llm = llm,
        query_prompt_template = query_prompt_template,
        database=':memory:'
    )

    return fsq_chat_bot

## Process Query

if __name__ == "__main__":

    # query = "Tell me the count for all the points that are related to manufacturing?"
    # query = "List down some coffee shops in Jodhpur?"

    question = "List petrol pumps in Chennai."
    fsq_chat_bot = initiate_chat_bot()
    state = fsq_chat_bot.process_question(question=question)['state']
    print("Generated Query:\n", state.query)
    print("Query Result:\n", state.result)
    print("Final Answer:\n", state.answer)