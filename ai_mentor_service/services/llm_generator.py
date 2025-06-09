import logging
from openai import OpenAI
import config

logger = logging.getLogger(__name__)


def generate_assignment_prompt(topic: str, subtopic: str = None, level: str = "A2") -> str:
    return (
        f"Сгенерируй теоретическое объяснение и одно упражнение по английскому языку\n"
        f"для уровня {level} по теме '{topic}'"
        + (f" и подтеме '{subtopic}'" if subtopic else "") + ".\n"
        "Структура ответа:\n"
        "THEORY:\n[текст теории]\n\nEXERCISE:\n[текст задания с вопросом и вариантами ответа]"
    )


def generate_assignment_content(topic: str, subtopic: str = None, level: str = "A2") -> dict:
    prompt = generate_assignment_prompt(topic, subtopic, level)
    logger.debug("LLM prompt: %s", prompt)

    try:
        client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Ты — учитель английского. Генерируй полезные и понятные теории и упражнения по английскому языку. Строго следуй запрошенной структуре."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7
        )
        full_text = response.choices[0].message.content.strip()
        logger.info("Сгенерировано задание через LLM")

        parts = full_text.split("EXERCISE:")
        theory = parts[0].replace("THEORY:", "").strip()
        exercise = parts[1].strip() if len(parts) > 1 else ""

        return {
            "topic": topic,
            "subtopic": subtopic,
            "level": level,
            "theory": theory,
            "exercise": exercise,
            "source": "llm"
        }

    except Exception as e:
        logger.exception("Ошибка генерации задания: %s", e)
        return {}
