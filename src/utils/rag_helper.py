from src.managers.profile_manager import get_user_profile
user_profile = get_user_profile()

def generate_rag_based_prompt(
    current_q: dict,
    user_profile: dict,
    previous_summary: str = "",
    rag_context: str = ""
) -> str:
    ...
