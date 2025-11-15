# db_prompts.py
from supabase import create_client
import config

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def get_agent_prompt(agent_name):
    """Достает промпт агента из базы"""
    try:
        response = supabase.table('agent_prompts')\
            .select('prompt_text')\
            .eq('agent_name', agent_name)\
            .execute()
        
        if response.data:
            return response.data[0]['prompt_text']
        else:
            return f"Промпт для {agent_name} не найден"
            
    except Exception as e:
        print(f"Ошибка базы: {e}")
        return f"Промпт для {agent_name} (ошибка загрузки)"