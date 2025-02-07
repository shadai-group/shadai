from enum import Enum


class AIModels(str, Enum):
    # Anthropic Models
    CLAUDE_3_5_SONNET_V2 = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    CLAUDE_3_5_SONNET = "us.anthropic.claude-3-5-sonnet-20240620-v1:0"
    CLAUDE_3_5_HAIKU = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    CLAUDE_3_OPUS = "us.anthropic.claude-3-opus-20240229-v1:0"
    CLAUDE_3_SONNET = "us.anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_HAIKU = "us.anthropic.claude-3-haiku-20240307-v1:0"

    # Meta Models
    LLAMA_3_2_1B_INSTRUCT = "us.meta.llama3-2-1b-instruct-v1:0"
    LLAMA_3_1_70B_INSTRUCT = "us.meta.llama3-1-70b-instruct-v1:0"
    LLAMA_3_1_8B_INSTRUCT = "us.meta.llama3-1-8b-instruct-v1:0"
