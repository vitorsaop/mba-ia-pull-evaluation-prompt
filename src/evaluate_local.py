"""
Avaliador LOCAL — não usa o LangSmith Hub.

Lê prompts/bug_to_user_story_v2.yml diretamente, monta o ChatPromptTemplate,
roda contra datasets/bug_to_user_story.jsonl e imprime as 5 métricas
(F1-Score, Clarity, Precision, Helpfulness, Correctness) exemplo a exemplo.

Use durante a iteração do prompt para não poluir o Hub com versões intermediárias.
Quando a média das 5 métricas atingir 0.9 ou mais, rode src/push_prompts.py
e depois src/evaluate.py (oficial, que puxa do Hub).
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

from utils import format_score, get_llm, load_yaml  # noqa: E402
from metrics import (  # noqa: E402
    evaluate_clarity,
    evaluate_f1_score,
    evaluate_precision,
)

load_dotenv()

YAML_PATH = "prompts/bug_to_user_story_v2.yml"
DATASET_PATH = "datasets/bug_to_user_story.jsonl"
PROMPT_KEY = "bug_to_user_story_v2"


def load_examples(jsonl_path: str) -> List[Dict[str, Any]]:
    examples: List[Dict[str, Any]] = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def build_chain(prompt_data: Dict[str, Any]):
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_data["system_prompt"]),
            ("human", prompt_data.get("user_prompt", "{bug_report}")),
        ]
    )
    return template | get_llm(temperature=0)


def main() -> int:
    provider = os.getenv("LLM_PROVIDER", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    eval_model = os.getenv("EVAL_MODEL", "gpt-4o")

    print("=" * 60)
    print("AVALIAÇÃO LOCAL — YAML direto, sem Hub")
    print("=" * 60)
    print(f"Provider:        {provider}")
    print(f"Modelo principal: {llm_model}")
    print(f"Modelo juiz:      {eval_model}")
    print(f"YAML:             {YAML_PATH}")
    print(f"Dataset:          {DATASET_PATH}\n")

    data = load_yaml(YAML_PATH)
    if not data or PROMPT_KEY not in data:
        print(f"Não foi possível carregar '{PROMPT_KEY}' em {YAML_PATH}")
        return 1

    chain = build_chain(data[PROMPT_KEY])
    examples = load_examples(DATASET_PATH)
    total = len(examples)
    print(f"Total de exemplos: {total}\n")

    f1s: List[float] = []
    clarities: List[float] = []
    precisions: List[float] = []

    print(f"{'#':>3}  {'F1':>5}  {'Clar':>5}  {'Prec':>5}  bug")
    print("-" * 60)

    for i, ex in enumerate(examples, 1):
        bug = ex["inputs"]["bug_report"]
        ref = ex["outputs"]["reference"]

        try:
            answer = chain.invoke({"bug_report": bug}).content
        except Exception as e:
            print(f"[{i:>2}/{total}] erro ao invocar chain: {e}")
            continue

        f1 = evaluate_f1_score(bug, answer, ref)["score"]
        clarity = evaluate_clarity(bug, answer, ref)["score"]
        precision = evaluate_precision(bug, answer, ref)["score"]

        f1s.append(f1)
        clarities.append(clarity)
        precisions.append(precision)

        snippet = bug.splitlines()[0][:55]
        print(f"{i:>3}  {f1:>5.2f}  {clarity:>5.2f}  {precision:>5.2f}  {snippet}")

    if not f1s:
        print("\nNenhum exemplo foi avaliado.")
        return 1

    avg_f1 = sum(f1s) / len(f1s)
    avg_clarity = sum(clarities) / len(clarities)
    avg_precision = sum(precisions) / len(precisions)
    helpfulness = (avg_clarity + avg_precision) / 2
    correctness = (avg_f1 + avg_precision) / 2

    metrics = {
        "F1-Score": avg_f1,
        "Clarity": avg_clarity,
        "Precision": avg_precision,
        "Helpfulness": helpfulness,
        "Correctness": correctness,
    }
    mean_of_means = sum(metrics.values()) / len(metrics)

    print("\n" + "=" * 60)
    print("Resumo das 5 métricas (média dos 15 exemplos):")
    print("=" * 60)
    for name, value in metrics.items():
        print(f"  {name:<12} {format_score(value, threshold=0.9)}")

    all_above = all(v >= 0.9 for v in metrics.values())
    print("-" * 60)
    print(f"  MÉDIA das 5 métricas: {mean_of_means:.4f}")
    print(f"  Todas as métricas >= 0.9: {'SIM' if all_above else 'NÃO'}")
    print(f"  Média >= 0.9:             {'SIM' if mean_of_means >= 0.9 else 'NÃO'}")
    print("=" * 60)

    if mean_of_means >= 0.9:
        print("\nMédia OK. Próximo passo: python src/push_prompts.py")
        return 0
    print("\nMédia abaixo de 0.9. Ajustar o YAML e rodar novamente.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
