from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        *,
        instructions: str,
        prompt: str,
    ) -> str:
        """Generate text using an LLM provider."""
        raise NotImplementedError