from dataclasses import dataclass
import re


@dataclass
class InputGuardrailResult:
    is_allowed: bool
    reason: str | None = None


class InputGuardrail:

    PROMPT_INJECTION_PATTERNS = [
        r"\bignore\s+(all\s+)?(previous|prior|system|developer)\s+instructions?\b",
        r"\bignore\s+(all\s+)?previous\s+prompts?\b",
        r"\breveal\s+(the\s+)?system\s+prompt\b",
        r"\bshow\s+(me\s+)?(the\s+)?system\s+prompt\b",
        r"\bprint\s+(the\s+)?system\s+prompt\b",
        r"\bexpose\s+(hidden\s+)?instructions?\b",
        r"\bbypass\s+(the\s+)?(security|safety|guardrails?)\b",
    ]

    SQL_MUTATION_PATTERNS = [
        r"\bdrop\s+(table|database|schema)\b",
        r"\btruncate\s+table\b",
        r"\balter\s+table\b",
        r"\bdelete\s+from\b",
        r"\binsert\s+into\b",
        r"\bupdate\s+\w+\s+set\b",
        r"\bcreate\s+(table|database|role|user)\b",
        r"\bgrant\s+\w+\b",
        r"\brevoke\s+\w+\b",
    ]

    def check(
        self,
        question: str,
    ) -> InputGuardrailResult:

        normalized = question.strip().lower()

        if not normalized:
            return InputGuardrailResult(
                is_allowed=False,
                reason="Question cannot be empty.",
            )

        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(
                pattern,
                normalized,
                flags=re.IGNORECASE,
            ):
                return InputGuardrailResult(
                    is_allowed=False,
                    reason=(
                        "Potential prompt-injection "
                        "instruction detected."
                    ),
                )

        for pattern in self.SQL_MUTATION_PATTERNS:
            if re.search(
                pattern,
                normalized,
                flags=re.IGNORECASE,
            ):
                return InputGuardrailResult(
                    is_allowed=False,
                    reason=(
                        "Database modification requests "
                        "are not allowed."
                    ),
                )

        return InputGuardrailResult(
            is_allowed=True
        )