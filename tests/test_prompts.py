"""
Testes automatizados para validação do prompt otimizado v2.

Garante que `prompts/bug_to_user_story_v2.yml` atende aos requisitos
estruturais exigidos pelo desafio antes de fazer push para o LangSmith Hub.
"""
import re
import sys
from pathlib import Path

import pytest
import yaml

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure  # noqa: E402,F401  (importação exigida pelo desafio)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str) -> dict:
    """Carrega prompts do arquivo YAML."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt_data() -> dict:
    """Retorna o dicionário do prompt v2 carregado do YAML."""
    data = load_prompts(str(PROMPT_PATH))
    assert PROMPT_KEY in data, f"Chave '{PROMPT_KEY}' não encontrada em {PROMPT_PATH}"
    return data[PROMPT_KEY]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' ausente"
        system_prompt = prompt_data["system_prompt"]
        assert isinstance(system_prompt, str), "system_prompt deve ser string"
        assert system_prompt.strip(), "system_prompt está vazio"
        assert len(system_prompt) > 100, "system_prompt suspeitosamente curto"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product ...")."""
        system_prompt = prompt_data["system_prompt"].lower()
        has_role_intro = "você é" in system_prompt
        has_persona_keyword = any(
            keyword in system_prompt
            for keyword in ("product owner", "product manager", "engenheiro", "especialista")
        )
        assert has_role_intro, "Prompt não inicia com definição de persona ('Você é ...')"
        assert has_persona_keyword, (
            "Persona não menciona um papel relevante (Product Owner/Manager/Especialista)"
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data["system_prompt"]
        # Padrão "Como ... eu quero ... para que ..." é o template canônico de user story
        has_user_story_template = (
            "Como" in system_prompt
            and "eu quero" in system_prompt
            and "para que" in system_prompt
        )
        # Critérios de aceitação Dado/Quando/Então também caracterizam formato
        has_criteria_format = "Critérios de Aceitação" in system_prompt and (
            "Dado" in system_prompt and "Quando" in system_prompt and "Então" in system_prompt
        )
        assert has_user_story_template, "Formato canônico de user story não exigido no prompt"
        assert has_criteria_format, "Formato Dado/Quando/Então não exigido no prompt"

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (Few-shot)."""
        system_prompt = prompt_data["system_prompt"]
        # Contagem de exemplos pelo marcador "## Exemplo"
        example_count = len(re.findall(r"##\s*Exemplo", system_prompt))
        # Contagem de "Bug Report:" como pares de input
        bug_report_count = system_prompt.count("Bug Report:")
        # Contagem de user stories no padrão "Como ... eu quero ... para que ..."
        user_story_count = len(
            re.findall(r"Como\s+[^,]+?,\s*eu quero\s+.+?,\s*para que", system_prompt)
        )
        assert example_count >= 2, f"Mínimo 2 exemplos esperados, encontrados {example_count}"
        assert bug_report_count >= 2, (
            f"Mínimo 2 entradas 'Bug Report:' esperadas, encontradas {bug_report_count}"
        )
        assert user_story_count >= 2, (
            f"Mínimo 2 saídas no padrão de user story esperadas, encontradas {user_story_count}"
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que não existem marcadores `[TODO]` ou `TODO` esquecidos."""
        system_prompt = prompt_data["system_prompt"]
        user_prompt = prompt_data.get("user_prompt", "")
        full_text = f"{system_prompt}\n{user_prompt}"
        assert "[TODO]" not in full_text, "Marcador [TODO] encontrado no prompt"
        assert "TODO" not in full_text, "Texto 'TODO' encontrado no prompt"
        assert "FIXME" not in full_text, "Texto 'FIXME' encontrado no prompt"

    def test_minimum_techniques(self, prompt_data):
        """Verifica se ao menos 2 técnicas estão listadas em 'techniques_applied'."""
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list), "'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Mínimo 2 técnicas exigidas em metadata, encontradas {len(techniques)}: {techniques}"
        )
        joined = " ".join(techniques).lower()
        assert "few-shot" in joined or "few shot" in joined, (
            "Few-shot Learning é obrigatório e não foi listado"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
