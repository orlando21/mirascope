"""This module contains the type definition for the OpenAI call keyword arguments."""

from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

from ..base import BaseCallKwargs
from .call_params import OpenAICallParams


class OpenAICallKwargs(OpenAICallParams, BaseCallKwargs[ChatCompletionToolParam]):
    model: str
    messages: list[ChatCompletionMessageParam]