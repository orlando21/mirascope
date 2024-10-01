from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-8b-instant")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))