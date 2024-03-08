"""A prompt for recommending movies of a particular genre."""
from mirascope.openai import OpenAICallParams, OpenAIPrompt


class MovieRecommendationPrompt(OpenAIPrompt):
    """Please recommend a list of movies in the {genre} category."""

    genre: str

    call_params = OpenAICallParams(model="gpt-3.5-turbo")
