from mirascope.core import BaseMessageParam, vertex
from vertexai.generative_models import GenerationConfig


@vertex.call(
    "gemini-1.5-flash",
    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))