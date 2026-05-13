"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

YAML_PATH = "prompts/bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    print(f"\nFazendo push de: {prompt_name}")

    system_prompt = prompt_data["system_prompt"]
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")

    chat_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])

    description = prompt_data.get("description", "").strip()
    techniques = prompt_data.get("techniques_applied", [])
    tags = prompt_data.get("tags", [])

    readme_lines = [
        f"# {prompt_name}",
        "",
        description,
        "",
        "## Técnicas Aplicadas",
    ]
    readme_lines.extend(f"- {tech}" for tech in techniques)
    readme = "\n".join(readme_lines)

    try:
        url = hub.push(
            prompt_name,
            chat_template,
            new_repo_is_public=True,
            new_repo_description=description,
            readme=readme,
            tags=tags,
        )
        print(f"  Publicado: {url}")
        return True
    except Exception as e:
        print(f"  Erro ao publicar: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    for field in ("description", "system_prompt", "version"):
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    if "[TODO]" in system_prompt or "TODO" in system_prompt:
        errors.append("system_prompt ainda contém TODOs")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"
        )

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS PARA O LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")

    data = load_yaml(YAML_PATH)
    if not data or PROMPT_KEY not in data:
        print(f"Não foi possível ler '{PROMPT_KEY}' em {YAML_PATH}")
        return 1

    prompt_data = data[PROMPT_KEY]

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Validação falhou:")
        for err in errors:
            print(f"  - {err}")
        return 1

    prompt_name = f"{username}/{PROMPT_KEY}"
    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    if success:
        print("\nPush concluído com sucesso.")
        print(f"Verifique em: https://smith.langchain.com/hub/{prompt_name}")
        return 0

    print("\nPush falhou.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
