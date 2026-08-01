"""Prompt engineering templates and utilities."""

from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class PromptTemplate(Enum):
    """Prompt template types."""

    TASK_PLANNING = "task_planning"
    MEMORY_EXTRACTION = "memory_extraction"
    EMAIL_CLASSIFICATION = "email_classification"
    ENTITY_EXTRACTION = "entity_extraction"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"


class PromptTemplates:
    """Pre-defined prompt templates."""

    TASK_PLANNING = """You are a task planning assistant. Given the following information, extract and organize tasks.

User context: {user_context}
Input: {input}

Extract tasks with the following information:
- Title (concise)
- Description (detailed)
- Priority (high/medium/low)
- Due date (if mentioned)
- Dependencies (if any)

Format as JSON array of task objects."""

    MEMORY_EXTRACTION = """You are a memory extraction assistant. Extract important information to store in memory.

User context: {user_context}
Input: {input}

Extract the following:
- Key facts
- Important events
- People mentioned
- Dates and times
- Locations
- Action items

Format as JSON with categories."""

    EMAIL_CLASSIFICATION = """You are an email classification assistant. Classify the email into categories.

Email subject: {subject}
Email body: {body}
Sender: {sender}

Classify into:
- Category (work, personal, finance, social, other)
- Urgency (high, medium, low)
- Action required (yes/no)
- Summary (1-2 sentences)

Format as JSON."""

    ENTITY_EXTRACTION = """You are an entity extraction assistant. Extract entities from the text.

Text: {text}

Extract:
- People (names)
- Organizations
- Locations
- Dates
- Monetary amounts
- Phone numbers
- Email addresses

Format as JSON with entity types."""

    SUMMARIZATION = """You are a summarization assistant. Summarize the following text.

Text: {text}
Max length: {max_length} words

Provide a concise summary that captures the main points."""

    QUESTION_ANSWERING = """You are a question answering assistant. Answer the question based on the context.

Context: {context}
Question: {question}

Provide a clear, accurate answer. If the answer is not in the context, say so."""

    CODE_GENERATION = """You are a code generation assistant. Generate code based on the requirements.

Requirements: {requirements}
Language: {language}

Generate clean, well-commented code that meets the requirements."""

    REASONING = """You are a reasoning assistant. Think through the problem step by step.

Problem: {problem}
Context: {context}

Provide your reasoning and final answer."""


class PromptBuilder:
    """Build prompts from templates."""

    def __init__(self):
        """Initialize prompt builder."""
        self.templates = {
            PromptTemplate.TASK_PLANNING: PromptTemplates.TASK_PLANNING,
            PromptTemplate.MEMORY_EXTRACTION: PromptTemplates.MEMORY_EXTRACTION,
            PromptTemplate.EMAIL_CLASSIFICATION: PromptTemplates.EMAIL_CLASSIFICATION,
            PromptTemplate.ENTITY_EXTRACTION: PromptTemplates.ENTITY_EXTRACTION,
            PromptTemplate.SUMMARIZATION: PromptTemplates.SUMMARIZATION,
            PromptTemplate.QUESTION_ANSWERING: PromptTemplates.QUESTION_ANSWERING,
            PromptTemplate.CODE_GENERATION: PromptTemplates.CODE_GENERATION,
            PromptTemplate.REASONING: PromptTemplates.REASONING,
        }

    def build(
        self,
        template: PromptTemplate,
        variables: dict[str, Any]
    ) -> str:
        """Build prompt from template."""
        template_str = self.templates[template]
        return template_str.format(**variables)

    def build_system_message(self, template: PromptTemplate) -> str:
        """Build system message for template."""
        system_messages = {
            PromptTemplate.TASK_PLANNING: "You are a task planning assistant.",
            PromptTemplate.MEMORY_EXTRACTION: "You are a memory extraction assistant.",
            PromptTemplate.EMAIL_CLASSIFICATION: "You are an email classification assistant.",
            PromptTemplate.ENTITY_EXTRACTION: "You are an entity extraction assistant.",
            PromptTemplate.SUMMARIZATION: "You are a summarization assistant.",
            PromptTemplate.QUESTION_ANSWERING: "You are a question answering assistant.",
            PromptTemplate.CODE_GENERATION: "You are a code generation assistant.",
            PromptTemplate.REASONING: "You are a reasoning assistant.",
        }
        return system_messages.get(template, "You are a helpful assistant.")


class PromptOptimizer:
    """Optimize prompts for better performance."""

    @staticmethod
    def add_few_shot_examples(prompt: str, examples: list[dict[str, str]]) -> str:
        """Add few-shot examples to prompt."""
        examples_str = "\n".join(
            f"Example {i+1}:\nInput: {ex['input']}\nOutput: {ex['output']}\n"
            for i, ex in enumerate(examples)
        )
        return f"{examples_str}\n\n{prompt}"

    @staticmethod
    def add_chain_of_thought(prompt: str) -> str:
        """Add chain-of-thought instruction."""
        return f"{prompt}\n\nThink step by step and show your reasoning."

    @staticmethod
    def add_context(prompt: str, context: str) -> str:
        """Add context to prompt."""
        return f"Context: {context}\n\n{prompt}"

    @staticmethod
    def add_constraints(prompt: str, constraints: list[str]) -> str:
        """Add constraints to prompt."""
        constraints_str = "\n".join(f"- {c}" for c in constraints)
        return f"{prompt}\n\nConstraints:\n{constraints_str}"


# Global instances
prompt_builder = PromptBuilder()
prompt_optimizer = PromptOptimizer()
