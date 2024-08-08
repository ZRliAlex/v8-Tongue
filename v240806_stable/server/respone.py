from __future__ import annotations

from typing import List, Optional, Union, Dict
from typing_extensions import TypedDict, Literal

from pydantic import BaseModel, Field

class TokenizeInputRequest(BaseModel):
    model: Optional[str] = model_field
    input: str = Field(description="The input to tokenize.")

    model_config = {
        "json_schema_extra": {"examples": [{"input": "How many tokens in this query?"}]}
    }