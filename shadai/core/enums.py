from enum import Enum


class AIModels(str, Enum):
    # Amazon models
    AMAZON_NOVA_PRO = "amazon.nova-pro-v1:0"
    AMAZON_NOVA_LITE = "amazon.nova-lite-v1:0"
    AMAZON_NOVA_MICRO = "amazon.nova-micro-v1:0"

    # Anthropic Models
    CLAUDE_3_7_SONNET = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    CLAUDE_3_5_SONNET_V2 = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    CLAUDE_3_5_SONNET = "us.anthropic.claude-3-5-sonnet-20240620-v1:0"
    CLAUDE_3_5_HAIKU = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    CLAUDE_3_OPUS = "us.anthropic.claude-3-opus-20240229-v1:0"
    CLAUDE_3_SONNET = "us.anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_HAIKU = "us.anthropic.claude-3-haiku-20240307-v1:0"

    # Cohere Models
    COHERE_COMMAND_R_PLUS_V3 = "cohere/command-r-plus-08-2024"
    COHERE_COMMAND_R_PLUS_V2 = "cohere/command-r-plus-04-2024"
    COHERE_COMMAND_PLUS = "cohere.command-r-plus-v1:0"
    COHERE_COMMAND_R_V3 = "cohere/command-r-08-2024"
    COHERE_COMMAND_R_V2 = "cohere/command-r-03-2024"
    COHERE_COMMAND_R = "cohere.command-r-v1:0"
    COHERE_COMMAND_LIGHT = "cohere.command-light-text-v14"

    # Deepseek Models
    DEEPSEEK_R1_V1 = "us.deepseek.r1-v1:0"

    # Meta Models
    LLAMA_3_3_70B_INSTRUCT = "meta.llama3-3-70b-instruct-v1:0"
    LLAMA_3_2_1B_INSTRUCT = "us.meta.llama3-2-1b-instruct-v1:0"
    LLAMA_3_1_70B_INSTRUCT = "us.meta.llama3-1-70b-instruct-v1:0"
    LLAMA_3_1_8B_INSTRUCT = "us.meta.llama3-1-8b-instruct-v1:0"
