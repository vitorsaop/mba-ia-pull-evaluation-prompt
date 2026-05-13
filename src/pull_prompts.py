"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def extract_messages(prompt: ChatPromptTemplate) -> dict:
    system_text = ""
    user_text = ""

    for message in prompt.messages:
        message_type = message.__class__.__name__.lower()
        template_text = getattr(message.prompt, "template", "")

        if "system" in message_type:
            system_text = template_text
        elif "human" in message_type or "user" in message_type:
            user_text = template_text

    return {"system_prompt": system_text, "user_prompt": user_text}


def pull_prompts_from_langsmith() -> bool:
    print(f"Puxando prompt: {PROMPT_NAME}")

    try:
        prompt = hub.pull(PROMPT_NAME)
    except Exception as e:
        print(f"Erro ao puxar prompt do Hub: {e}")
        return False

    messages = extract_messages(prompt)

    prompt_dict = {
        "bug_to_user_story_v1": {
            "description": "Prompt original (v1) puxado do LangSmith Hub para refatoracao.",
            "system_prompt": messages["system_prompt"],
            "user_prompt": messages["user_prompt"],
            "version": "v1",
            "source": PROMPT_NAME,
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if save_yaml(prompt_dict, OUTPUT_PATH):
        print(f"Prompt salvo em: {OUTPUT_PATH}")
        return True

    print("Falha ao salvar o arquivo YAML.")
    return False


def main():
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
