# main.py
from langgraph.graph import StateGraph, START, END
from typing import Dict, Any

# 1. Определяем состояние (простой словарь)
class SimpleState(Dict[str, Any]):
    message: str

# 2. Создаем узлы (просто функции)
def first_node(state: SimpleState):
    print("Первый узел выполняется!")
    state["message"] = "Привет от первого узла"
    return state

def second_node(state: SimpleState):
    print("Второй узел выполняется!")
    state["message"] += " + привет от второго узла"
    return state

# 3. Собираем граф
graph = StateGraph(SimpleState)

# Добавляем узлы
graph.add_node("first", first_node)
graph.add_node("second", second_node)

# Создаем простую линейную цепочку: START -> first -> second -> END
graph.add_edge(START, "first")
graph.add_edge("first", "second")
graph.add_edge("second", END)

# Компилируем
app = graph.compile()

# 4. Запускаем
if __name__ == "__main__":
    print("Запускаем простой граф...")
    initial_state = {"message": "Начальное сообщение"}
    result = app.invoke(initial_state)
    print("\nРезультат:", result["message"])