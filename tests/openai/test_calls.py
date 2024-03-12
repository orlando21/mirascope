"""Tests for the `OpenAICall` class."""
from typing import Type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from mirascope.openai.calls import OpenAICall
from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import (
    OpenAICallParams,
    OpenAICallResponse,
    OpenAICallResponseChunk,
)


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_call_call(
    mock_create: MagicMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion: ChatCompletion,
) -> None:
    """Tests `OpenAIPrompt.create` returns the expected response when called."""
    mock_create.return_value = fixture_chat_completion
    kwargs = {"temperature": 0.8}
    response = fixture_openai_test_call.call(**kwargs)
    assert isinstance(response, OpenAICallResponse)
    mock_create.assert_called_once_with(
        model=fixture_openai_test_call.call_params.model,
        messages=fixture_openai_test_call.messages(),
        stream=False,
        temperature=kwargs["temperature"],
    )


@patch("openai.resources.chat.completions.Completions.create", new_callable=MagicMock)
def test_openai_call_call_with_tools(
    mock_create: MagicMock,
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_chat_completion_with_tools: ChatCompletion,
) -> None:
    """Tests that tools are properly passed to the create call."""
    mock_create.return_value = fixture_chat_completion_with_tools

    class CallWithTools(OpenAICall):
        template = "test"

        call_params = OpenAICallParams(model="gpt-4", tools=[fixture_my_openai_tool])

    call_with_tools = CallWithTools()
    response = call_with_tools.call()
    mock_create.assert_called_once_with(
        model="gpt-4",
        messages=call_with_tools.messages(),
        tools=[fixture_my_openai_tool.tool_schema()],
        stream=False,
    )
    assert response.tool_types == [fixture_my_openai_tool]


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_call_call_with_wrapper(
    mock_create: MagicMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion: ChatCompletion,
) -> None:
    """Tests `OpenAI` is created with a wrapper in `OpenAIPrompt.create`."""
    mock_create.return_value = fixture_chat_completion
    wrapper = MagicMock()
    wrapper.return_value = OpenAI(api_key="test")

    fixture_openai_test_call.call_params.wrapper = wrapper
    fixture_openai_test_call.call()
    wrapper.assert_called_once()


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_call_call_async(
    mock_create: AsyncMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion: ChatCompletion,
) -> None:
    """Tests `OpenAIPrompt.create` returns the expected response when called."""
    mock_create.return_value = fixture_chat_completion
    kwargs = {"temperature": 0.8}
    response = await fixture_openai_test_call.call_async(**kwargs)
    assert isinstance(response, OpenAICallResponse)
    mock_create.assert_called_once_with(
        model=fixture_openai_test_call.call_params.model,
        messages=fixture_openai_test_call.messages(),
        stream=False,
        temperature=kwargs["temperature"],
    )


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_call_call_async_with_wrapper(
    mock_create: AsyncMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion: ChatCompletion,
) -> None:
    """Tests `OpenAI` is created with a wrapper in `OpenAIPrompt.create`."""
    mock_create.return_value = fixture_chat_completion
    wrapper = MagicMock()
    wrapper.return_value = AsyncOpenAI(api_key="test")

    fixture_openai_test_call.call_params.wrapper_async = wrapper
    await fixture_openai_test_call.call_async()
    wrapper.assert_called_once()


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_call_stream(
    mock_create: MagicMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
):
    """Tests `OpenAIPrompt.stream` returns expected response."""
    mock_create.return_value = fixture_chat_completion_chunks

    stream = fixture_openai_test_call.stream()

    for i, chunk in enumerate(stream):
        assert isinstance(chunk, OpenAICallResponseChunk)
        assert chunk.chunk == fixture_chat_completion_chunks[i]

    mock_create.assert_called_once_with(
        model=fixture_openai_test_call.call_params.model,
        messages=fixture_openai_test_call.messages(),
        stream=True,
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_openai_call_stream_with_wrapper(
    mock_create: MagicMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
) -> None:
    """Tests `OpenAI` is created with a wrapper in `OpenAIPrompt.create`."""
    mock_create.return_value = fixture_chat_completion_chunks
    wrapper = MagicMock()
    wrapper.return_value = OpenAI(api_key="test")

    fixture_openai_test_call.call_params.wrapper = wrapper
    stream = fixture_openai_test_call.stream()
    for _ in stream:
        pass
    wrapper.assert_called_once()


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_prompt_stream_async(
    mock_create: AsyncMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
):
    """Tests `OpenAIPrompt.stream` returns expected response."""
    mock_create.return_value.__aiter__.return_value = fixture_chat_completion_chunks

    stream = fixture_openai_test_call.stream_async()

    i = 0
    async for chunk in stream:
        assert isinstance(chunk, OpenAICallResponseChunk)
        assert chunk.chunk == fixture_chat_completion_chunks[i]
        i += 1

    mock_create.assert_called_once_with(
        model=fixture_openai_test_call.call_params.model,
        messages=fixture_openai_test_call.messages(),
        stream=True,
    )


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_call_stream_async_with_wrapper(
    mock_create: AsyncMock,
    fixture_openai_test_call: OpenAICall,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
) -> None:
    """Tests `OpenAI` is created with a wrapper in `OpenAIPrompt.create`."""
    mock_create.return_value.__aiter__.return_value = fixture_chat_completion_chunks
    wrapper = MagicMock()
    wrapper.return_value = AsyncOpenAI(api_key="test")

    fixture_openai_test_call.call_params.wrapper_async = wrapper
    stream = fixture_openai_test_call.stream_async()
    async for _ in stream:
        pass
    wrapper.assert_called_once()
