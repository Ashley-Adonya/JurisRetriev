from pathlib import Path


PROMPT_FOLDER_NAME = "prompt"
DEFAULT_MODE = "defense_expert"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_prompts_dir() -> Path:
    return _project_root() / PROMPT_FOLDER_NAME


def list_prompt_modes() -> list[str]:
    prompts_dir = get_prompts_dir()
    if not prompts_dir.exists():
        return []
    return sorted([p.stem for p in prompts_dir.glob("*.txt") if p.stem != "query_rewrite"])


def read_prompt_file(prompt_name: str) -> str:
    prompt_file = get_prompts_dir() / f"{prompt_name}.txt"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt introuvable: {prompt_file}")
    return prompt_file.read_text(encoding="utf-8").strip()


def get_system_prompt(mode: str = DEFAULT_MODE) -> str:
    available_modes = list_prompt_modes()
    if mode not in available_modes:
        mode = DEFAULT_MODE
    return read_prompt_file(mode)


def get_query_rewrite_prompt() -> str:
    return read_prompt_file("query_rewrite")
