from mirascope.core import BaseDynamicConfig, azure, prompt_template


@azure.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> BaseDynamicConfig:
    return {
        "call_params": {"max_tokens": 512},
        "metadata": {"tags": {"version:0001"}},
    }


print(recommend_book("fantasy"))