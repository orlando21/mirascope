from mistralai.client import MistralClient
from mistralai.models.chat_completion import ToolChoice
from pydantic import BaseModel

client = MistralClient()


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


def extract_book(text: str) -> Book:
    completion = client.chat(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": f"Extract {text}"}],
        tools=[
            {
                "function": {
                    "name": "Book",
                    "description": "An extracted book.",
                    "parameters": {
                        "properties": {
                            "title": {"type": "string"},
                            "author": {"type": "string"},
                        },
                        "required": ["title", "author"],
                        "type": "object",
                    },
                },
                "type": "function",
            }
        ],
        tool_choice=ToolChoice.any,
    )
    if tool_calls := completion.choices[0].message.tool_calls:
        return Book.model_validate_json(tool_calls[0].function.arguments)
    raise ValueError("No tool call found")


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'