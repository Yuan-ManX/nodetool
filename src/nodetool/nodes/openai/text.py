import numpy as np
from nodetool.metadata.types import ImageRef, Provider, Tensor
from nodetool.metadata.types import TextRef
from nodetool.workflows.base_node import BaseNode
from nodetool.metadata.types import GPTModel
from nodetool.workflows.processing_context import ProcessingContext

from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai.types.create_embedding_response import CreateEmbeddingResponse
from pydantic import Field

from enum import Enum


class EmbeddingModel(str, Enum):
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"


class ResponseFormat(str, Enum):
    JSON_OBJECT = "json_object"
    TEXT = "text"


class Embedding(BaseNode):
    """
    Generate vector representations of text for semantic analysis.
    embeddings, similarity, search, clustering, classification

    Uses OpenAI's embedding models to create dense vector representations of text.
    These vectors capture semantic meaning, enabling:
    - Semantic search
    - Text clustering
    - Document classification
    - Recommendation systems
    - Anomaly detection
    - Measuring text similarity and diversity
    """

    input: str | TextRef = Field(title="Input", default="")
    model: EmbeddingModel = Field(
        title="Model", default=EmbeddingModel.TEXT_EMBEDDING_3_SMALL
    )
    chunk_size: int = 4096

    async def process(self, context: ProcessingContext) -> Tensor:
        input = await context.text_to_str(self.input)
        # chunk the input into smaller pieces
        chunks = [
            input[i : i + self.chunk_size]
            for i in range(0, len(input), self.chunk_size)
        ]

        response = await context.run_prediction(
            self.id,
            provider=Provider.OpenAI,
            params={"input": chunks},
            model=self.model.value,
        )

        res = CreateEmbeddingResponse(**response)

        all = [i.embedding for i in res.data]
        avg = np.mean(all, axis=0)
        return Tensor.from_numpy(avg)


class GPT(BaseNode):
    """
    Generate natural language responses using GPT models.
    llm, text-generation, chatbot, question-answering

    Leverages OpenAI's GPT models to:
    - Generate human-like text responses
    - Answer questions
    - Complete prompts
    - Engage in conversational interactions
    - Assist with writing and editing tasks
    - Perform text analysis and summarization
    """

    model: GPTModel = Field(title="Model", default=GPTModel.GPT3)
    system: str = Field(title="System", default="You are a friendly assistant.")
    prompt: str = Field(title="Prompt", default="")
    image: ImageRef = Field(title="Image", default=ImageRef())
    presence_penalty: float = Field(
        title="Presence Penalty", default=0.0, ge=(-2.0), le=2.0
    )
    frequency_penalty: float = Field(
        title="Frequency Penalty", default=0.0, ge=(-2.0), le=2.0
    )
    temperature: float = Field(title="Temperature", default=1.0, ge=0.0, le=2.0)
    max_tokens: int = Field(title="Max Tokens", default=100, ge=1, le=2048)
    top_p: float = Field(title="Top P", default=1.0, ge=0.0, le=1.0)

    async def process(self, context: ProcessingContext) -> str:
        content = []
        if not self.image.is_empty():
            base64_image = await context.image_to_base64(self.image)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                }
            )

        content.append(
            {
                "type": "text",
                "text": self.prompt,
            }
        )

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": content},
        ]

        response = await context.run_prediction(
            node_id=self.id,
            provider=Provider.OpenAI,
            params={
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "presence_penalty": self.presence_penalty,
                "frequency_penalty": self.frequency_penalty,
            },
            model=self.model.value,
        )

        res = ChatCompletion(**response)

        assert len(res.choices) > 0
        assert res.choices[0].message.content is not None
        return res.choices[0].message.content
