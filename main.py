import re
from dataclasses import dataclass
from typing import Callable, Dict, Any

@dataclass
class Step:
    name: str
    template: str
    validator: Callable[[str], bool]

def mock_llm(prompt: str) -> str:
    topic_match = re.search(r'TOPIC=(.*)', prompt)
    text_match = re.search(r'TEXT=(.*)', prompt)
    topic = topic_match.group(1).strip() if topic_match else 'unknown'
    text = text_match.group(1).strip() if text_match else ''
    if 'extract' in prompt.lower():
        words = re.findall(r'[A-Z][a-z]+', text)
        return ', '.join(dict.fromkeys(words)) or 'NoEntities'
    if 'summarize' in prompt.lower():
        return f'Summary about {topic}: {text[:80]}'
    return f'Action: review {topic}'

def required(text: str) -> bool:
    return bool(text.strip())

def not_empty_list(text: str) -> bool:
    return bool(text.strip()) and text != 'NoEntities'

def run_workflow(input_text: str, topic: str) -> Dict[str, Any]:
    steps = [
        Step('extract', 'extract entities from TEXT={input}', not_empty_list),
        Step('summarize', 'summarize TEXT={input} about TOPIC={topic}', required),
        Step('action', 'suggest next action about TOPIC={topic}', required),
    ]
    context = {'input': input_text, 'topic': topic}
    results = {}
    for step in steps:
        prompt = step.template.format(**context)
        output = mock_llm(prompt)
        if not step.validator(output):
            raise ValueError(f'Step {step.name} failed validation')
        results[step.name] = output
        context[step.name] = output
    return results

if __name__ == '__main__':
    data = 'OpenAI released a new model for workflow automation in Berlin.'
    print(run_workflow(data, 'AI workflow automation'))