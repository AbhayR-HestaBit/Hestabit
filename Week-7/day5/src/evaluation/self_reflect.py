import json
import logging
from typing import Dict

from src.generator.llm_client import LocalLLMClient


logger = logging.getLogger(__name__)


class SelfReflector:
    def __init__(self, llm_client: LocalLLMClient) -> None:
        self.llm = llm_client

    def critique(self, question: str, answer: str, context: str) -> Dict:
        prompt = (
            "[INST] <<SYS>>\n"
            "You are an impartial judge. Your task is to evaluate if an answer is grounded in the provided context.\n"
            "CRITICAL RULES:\n"
            "1. If the answer says 'I don't know' and the information is TRULY NOT in the context, give it a score of 10.\n"
            "2. If the answer provides facts NOT in the context, give it a score of 1 (hallucination).\n"
            "3. If the answer uses outside knowledge, give it a score of 1.\n"
            "<</SYS>>\n\n"
            f"Context: {context[:4000]}\n"
            f"Question: {question}\n"
            f"Answer: {answer}\n"
            'Rate from 1-10. Return ONLY valid JSON:\n'
            '{"score":N,"issues":["..."],"improved_answer":"..."} [/INST]'
        )

        raw = self.llm.generate(prompt)
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end != -1:
                candidate = raw[start:end]
            else:
                candidate = raw
            parsed = json.loads(candidate)

            score = int(parsed.get("score", 5))
            issues = parsed.get("issues", [])
            improved = parsed.get("improved_answer", answer)
            if not isinstance(issues, list):
                issues = [str(issues)]
            return {
                "score": score,
                "issues": issues,
                "improved_answer": improved or answer,
            }
        except Exception as exc:
            logger.warning("SelfReflector JSON parse failed: %s", exc)
            return {"score": 5, "issues": [], "improved_answer": answer}

    def refine_if_needed(
        self, question: str, answer: str, context: str, min_score: int = 7
    ) -> str:
        result = self.critique(question, answer, context)
        score = result.get("score", 5)
        improved = result.get("improved_answer", answer)

        if score < min_score:
            logger.warning(
                "Answer score %s < %s, refining", score, min_score
            )
            return improved or answer
        return answer

