import json
import logging
from typing import Dict, Any, Optional

from src.generator.llm_client import LocalLLMClient

# Configure logging
logger = logging.getLogger(__name__)


class SelfReflector:
    def __init__(self, llm_client: LocalLLMClient) -> None:
        self.llm = llm_client

    def critique(self, question: str, answer: str, context: str) -> Dict[str, Any]:
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

        try:
            raw = self.llm.generate(prompt)
            if not raw:
                logger.warning("LLM returned empty response for self-reflection.")
                return {"score": 5, "issues": ["Empty LLM response"], "improved_answer": answer}

            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end != -1:
                candidate = raw[start:end]
            else:
                candidate = raw
                
            parsed = json.loads(candidate)
            
            # Extract and validate fields
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
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse self-reflection JSON: {e}. Raw response: {raw[:100]}...")
            return {"score": 5, "issues": ["JSON parse error"], "improved_answer": answer}
        except Exception as exc:
            logger.error(f"SelfReflector critique failed: {exc}")
            return {"score": 5, "issues": [str(exc)], "improved_answer": answer}

    def refine_if_needed(
        self, question: str, answer: str, context: str, min_score: int = 7
    ) -> str:
            result = self.critique(question, answer, context)
            score = result.get("score", 5)
            improved = result.get("improved_answer", answer)
    
            if score < min_score:
                logger.warning(f"Answer score {score} < {min_score}, using improved version.")
                return improved or answer
            return answer
        except Exception as e:
            logger.error(f"Refinement process failed: {e}")
            return answer

