"""This module contains the `MistralCallResponse` class."""

from mistralai.models.chat_completion import (
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatMessage,
    ToolCall,
)
from mistralai.models.common import UsageInfo
from pydantic import computed_field

from ..base import BaseCallResponse, BaseMessageParam
from .call_params import MistralCallParams
from .dynamic_config import MistralDynamicConfig
from .tool import MistralTool


class MistralCallResponse(
    BaseCallResponse[
        ChatCompletionResponse,
        MistralTool,
        MistralDynamicConfig,
        BaseMessageParam,
        MistralCallParams,
        BaseMessageParam,
    ]
):
    '''A convenience wrapper around the Mistral `ChatCompletion` response.

    When calling the Mistral API using a function decorated with `mistral_call`, the
    response will be an `MistralCallResponse` instance with properties that allow for
    more convenience access to commonly used attributes.

    Example:

    ```python
    from mirascope.core.mistral import mistral_call

    @mistral_call(model="gpt-4o")
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    response = recommend_book("fantasy")  # response is an `MistralCallResponse` instance
    print(response.content)
    #> Sure! I would recommend...
    ```
    '''

    _provider = "mistral"

    @computed_field
    @property
    def message_param(self) -> BaseMessageParam:
        """Returns the assistants's response as a message parameter."""
        return self.message.model_dump()  # type: ignore

    @property
    def choices(self) -> list[ChatCompletionResponseChoice]:
        """Returns the array of chat completion choices."""
        return self.response.choices

    @property
    def choice(self) -> ChatCompletionResponseChoice:
        """Returns the 0th choice."""
        return self.choices[0]

    @property
    def message(self) -> ChatMessage:
        """Returns the message of the chat completion for the 0th choice."""
        return self.choice.message

    @property
    def content(self) -> str:
        """The content of the chat completion for the 0th choice."""
        content = self.message.content
        # We haven't seen the `list[str]` response type in practice, so for now we
        # return the first item in the list
        return content if isinstance(content, str) else content[0]

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.response.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.response.id

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [
            choice.finish_reason if choice.finish_reason else ""
            for choice in self.choices
        ]

    @property
    def tool_calls(self) -> list[ToolCall] | None:
        """Returns the tool calls for the 0th choice message."""
        return self.message.tool_calls

    @computed_field
    @property
    def tools(self) -> list[MistralTool] | None:
        """Returns the tools for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if not self.tool_types or not self.tool_calls:
            return None

        extracted_tools = []
        for tool_call in self.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function.name == tool_type._name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @computed_field
    @property
    def tool(self) -> MistralTool | None:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if tools := self.tools:
            return tools[0]
        return None

    @classmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[MistralTool, str]]
    ) -> list[BaseMessageParam]:
        """Returns the tool message parameters for tool call results."""
        return [
            {
                "role": "tool",
                "content": output,
                "tool_call_id": tool.tool_call.id,
                "name": tool._name(),
            }  # type: ignore
            for tool, output in tools_and_outputs
        ]

    @property
    def usage(self) -> UsageInfo:
        """Returns the usage of the chat completion."""
        return self.response.usage

    @property
    def input_tokens(self) -> int:
        """Returns the number of input tokens."""
        return self.usage.prompt_tokens

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        return self.usage.completion_tokens