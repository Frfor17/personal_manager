# main.py
import requests
from langgraph.graph import StateGraph, START, END
from typing import Dict, Any
import config
from db_prompts import get_agent_prompt

class SimpleState(Dict[str, Any]):
    user_input: str
    category: str              # "finance", "health", "general"
    finance_response: str      # ответ финансового агента
    health_response: str       # ответ медицинского агента  
    general_response: str      # ответ общего агента
    final_response: str        # финальный ответ для бота

# 2. Функция для вызова LLM через OpenRouter
def call_openrouter(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "tngtech/deepseek-r1t2-chimera:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(config.OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]
        
        # Очищаем ответ от [BOS] и [EOS] токенов
        result = result.replace('[BOS]', '').replace('[EOS]', '').strip()
        
        # Проверяем что ответ не пустой
        if not result or result.isspace():
            return "Извините, не удалось получить ответ. Попробуйте задать вопрос по-другому."
        
        return result
        
    except Exception as e:
        print(f"Ошибка API: {e}")
        return "Произошла ошибка при обращении к AI. Попробуйте позже."

# 3. Создаем узлы графа
def first_classifier_agent(state: SimpleState):
    user_message = state["user_input"]
    
    # Берем промпт из базы вместо хардкода
    base_prompt = get_agent_prompt('classifier')
    prompt = f"{base_prompt}\n\nВОПРОС: {user_message}\n\nОТВЕТ:"
    
    print("Классификатор определяет категорию...")
    category = call_openrouter(prompt).strip().lower()


    # Очищаем ответ
    category = category.replace('"', '').replace("'", "").strip()

    # Проверяем что категория валидная
    if category not in ["finance", "health", "general"]:
        category = "general"  # fallback

    state["category"] = category
    print(f"Определена категория: {category}")
    return state

def router(state: SimpleState):
    """Решает, куда отправить запрос после классификатора"""
    category = state["category"]
    
    if category == "finance":
        return "finance_agent"
    elif category == "health":
        return "health_agent"
    else:
        return "general_agent"

def second_finance_agent(state: SimpleState):
    # Берем данные из state
    user_question = state["user_input"]
    
    # Промпт из базы
    base_prompt = get_agent_prompt('finance_agent')
    prompt = f"{base_prompt}\n\nВОПРОС: {user_question}\n\nОТВЕТ:"
    
    response = call_openrouter(prompt)
    state["finance_response"] = response  # Записываем ответ в state
    state["final_response"] = response  # ← ВАЖНО: пишем в финальный ответ
    return state


def third_health_agent(state: SimpleState):
    # Берем данные из state
    user_question = state["user_input"]
    
    # Промпт из базы
    base_prompt = get_agent_prompt('health_agent')
    prompt = f"{base_prompt}\n\nВОПРОС: {user_question}\n\nОТВЕТ:"
    
    response = call_openrouter(prompt)
    state["health_response"] = response  # Записываем ответ в state
    state["final_response"] = response  # ← ВАЖНО: пишем в финальный ответ
    return state

def general_agent(state: SimpleState):
    user_question = state["user_input"]
    
    # Промпт из базы
    base_prompt = get_agent_prompt('general_agent')
    prompt = f"{base_prompt}\n\nВОПРОС: {user_question}\n\nОТВЕТ:"
    
    response = call_openrouter(prompt)
    state["general_response"] = response
    state["final_response"] = response  # записываем финальный ответ
    return state

def print_node(state: SimpleState):
    print("Печатаем результат:")
    print(f"Пользователь: {state['user_input']}")
    print(f"LLM: {state['llm_response']}")
    return state

# 4. Собираем граф
graph = StateGraph(SimpleState)

# собираем всех агентов
graph.add_node("classifier", first_classifier_agent)
graph.add_node("finance_agent", second_finance_agent)
graph.add_node("health_agent", third_health_agent)
graph.add_node("general_agent", general_agent)  # можно переиспользовать или создать отдельного

# Стартуем с классификатора
graph.add_edge(START, "classifier")

# От классификатора идем к нужному агенту через маршрутизатор
graph.add_conditional_edges(
    "classifier",
    router,  # функция которая решает куда дальше
    {
        "finance_agent": "finance_agent",
        "health_agent": "health_agent", 
        "general_agent": "general_agent"
    }
)

# Все спецагенты идут в конец
graph.add_edge("finance_agent", END)
graph.add_edge("health_agent", END) 
graph.add_edge("general_agent", END)

app = graph.compile()

# 5. Запускаем
if __name__ == "__main__":
    print("Запускаем простой граф с OpenRouter...")
    
    initial_state = {
        "user_input": "Привет! Напиши короткое приветствие на русском.",
        "llm_response": ""
    }
    
    result = app.invoke(initial_state)
    print("\nГотово!")