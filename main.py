# main.py
import requests
from langgraph.graph import StateGraph, START, END
from typing import Dict, Any
import config  # импортируем твой конфиг

# 1. Определяем состояние
class SimpleState(Dict[str, Any]):
    user_input: str
    llm_response: str

# 2. Функция для вызова LLM через OpenRouter
def call_openrouter(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistralai/mistral-7b-instruct:free",  # бесплатная модель
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(config.OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Ошибка: {str(e)}"

# 3. Создаем узлы графа
def llm_node(state: SimpleState):
    print("Отправляем запрос к LLM...")
    response = call_openrouter(state["user_input"])
    state["llm_response"] = response
    return state

def print_node(state: SimpleState):
    print("Печатаем результат:")
    print(f"Пользователь: {state['user_input']}")
    print(f"LLM: {state['llm_response']}")
    return state

# 4. Собираем граф
graph = StateGraph(SimpleState)
graph.add_node("llm", llm_node)
graph.add_node("print", print_node)

# Простая линейная цепочка
graph.add_edge(START, "llm")
graph.add_edge("llm", "print")
graph.add_edge("print", END)

app = graph.compile()

# 5. Запускаем
if __name__ == "__main__":
    print("Запускаем простой граф с OpenRouter...")
    
    # Можно менять запрос здесь
    initial_state = {
        "user_input": "Привет! Напиши короткое приветствие на русском.",
        "llm_response": ""
    }
    
    result = app.invoke(initial_state)
    print("\nГотово!")