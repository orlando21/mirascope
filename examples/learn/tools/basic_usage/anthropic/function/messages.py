from mirascope.core import Messages, anthropic


def get_book_author(title: str) -> str:
    """Returns the author of the book with the given title

    Args:
        title: The title of the book.
    """
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"


@anthropic.call("claude-3-5-sonnet-20240620", tools=[get_book_author])
def identify_author(book: str) -> Messages.Type:
    return Messages.User(f"Who wrote {book}?")


response = identify_author("The Name of the Wind")
if tool := response.tool:
    print(tool.call())
    print(f"Original tool call: {tool.tool_call}")
else:
    print(response.content)