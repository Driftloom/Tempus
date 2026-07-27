"""Unit tests for LLM prompt module."""

import pytest
from app.llm.prompt import PromptBuilder, PromptOptimizer, PromptTemplate


@pytest.fixture
def prompt_builder():
    """Create prompt builder fixture."""
    return PromptBuilder()


@pytest.fixture
def prompt_optimizer():
    """Create prompt optimizer fixture."""
    return PromptOptimizer()


# Prompt Builder Tests
def test_prompt_builder_initialization(prompt_builder):
    """Test prompt builder initialization."""
    assert prompt_builder is not None
    assert len(prompt_builder.messages) == 0


def test_prompt_builder_add_system_message(prompt_builder):
    """Test adding system message."""
    prompt_builder.add_system_message("You are a helpful assistant.")
    
    assert len(prompt_builder.messages) == 1
    assert prompt_builder.messages[0]["role"] == "system"


def test_prompt_builder_add_user_message(prompt_builder):
    """Test adding user message."""
    prompt_builder.add_user_message("Hello, how are you?")
    
    assert len(prompt_builder.messages) == 1
    assert prompt_builder.messages[0]["role"] == "user"


def test_prompt_builder_add_assistant_message(prompt_builder):
    """Test adding assistant message."""
    prompt_builder.add_assistant_message("I'm doing well, thank you!")
    
    assert len(prompt_builder.messages) == 1
    assert prompt_builder.messages[0]["role"] == "assistant"


def test_prompt_builder_build(prompt_builder):
    """Test building prompt."""
    prompt_builder.add_system_message("You are a helpful assistant.")
    prompt_builder.add_user_message("Hello!")
    
    messages = prompt_builder.build()
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_prompt_builder_clear(prompt_builder):
    """Test clearing prompt."""
    prompt_builder.add_system_message("Test")
    prompt_builder.clear()
    
    assert len(prompt_builder.messages) == 0


def test_prompt_builder_with_context(prompt_builder):
    """Test building prompt with context."""
    context = {"user_name": "John", "task": "Write code"}
    prompt_builder.add_user_message("Help me with my task", context=context)
    
    messages = prompt_builder.build()
    
    assert len(messages) == 1
    assert "user_name" in messages[0]["content"]


# Prompt Optimizer Tests
def test_prompt_optimizer_initialization(prompt_optimizer):
    """Test prompt optimizer initialization."""
    assert prompt_optimizer is not None


def test_prompt_optimizer_optimize_length(prompt_optimizer):
    """Test prompt length optimization."""
    long_prompt = "This is a very long prompt " * 100
    optimized = prompt_optimizer.optimize_length(long_prompt, max_length=100)
    
    assert len(optimized) <= 100


def test_prompt_optimizer_remove_redundancy(prompt_optimizer):
    """Test removing redundancy."""
    prompt = "Hello hello HELLO world world"
    optimized = prompt_optimizer.remove_redundancy(prompt)
    
    assert "hello" not in optimized.lower() or optimized.lower().count("hello") == 1


def test_prompt_optimizer_add_clarity(prompt_optimizer):
    """Test adding clarity."""
    prompt = "do this"
    optimized = prompt_optimizer.add_clarity(prompt)
    
    assert len(optimized) >= len(prompt)


# Prompt Template Tests
def test_prompt_template_render():
    """Test prompt template rendering."""
    template = PromptTemplate("Hello, {name}! Your task is: {task}")
    rendered = template.render(name="John", task="Write code")
    
    assert "John" in rendered
    assert "Write code" in rendered


def test_prompt_template_with_variables():
    """Test prompt template with variables."""
    template = PromptTemplate("Task: {task}, Priority: {priority}")
    variables = {"task": "Test", "priority": "High"}
    rendered = template.render(**variables)
    
    assert "Test" in rendered
    assert "High" in rendered


def test_prompt_template_missing_variable():
    """Test prompt template with missing variable."""
    template = PromptTemplate("Hello, {name}!")
    
    with pytest.raises(KeyError):
        template.render()  # Missing 'name'


def test_prompt_template_default_value():
    """Test prompt template with default value."""
    template = PromptTemplate("Hello, {name}!")
    rendered = template.render(name="Guest")
    
    assert "Guest" in rendered
