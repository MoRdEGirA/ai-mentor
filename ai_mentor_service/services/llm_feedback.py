from openai import OpenAI
import config
import logging

logger = logging.getLogger(__name__)

def generate_feedback_text(name: str, mood: dict, topic: str = None, answers: list = None) -> str:
    try:
        mood_summary = (
            f"стресс: {mood.get('score_stress', 'нет данных')}, "
            f"тревожность: {mood.get('score_anxiety', 'нет данных')}, "
            f"позитив: {mood.get('score_positive', 'нет данных')}, "
            f"энергия: {mood.get('score_energy', 'нет данных')}"
        )

        answer_summary = ""
        if answers:
            answer_summary = "Ответы пользователя: " + ", ".join(answers)

        prompt = (
            f"Имя: {name}\n"
            f"Настроение: {mood_summary}\n"
            f"{'Тема задания: ' + topic if topic else ''}\n"
            f"{answer_summary}\n\n"
            "Сгенерируй короткий (3-7 предложений) эмпатичный отзыв от ИИ-наставника после выполнения задания. "
            "Обязательно учитывай эмоциональное состояние и постарайся поддержать, мотивировать и внушить уверенность."
        )

        client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": (
                    "Ты — эмпатичный и внимательный ИИ-ментор, который всегда поддерживает студента. "
                    "Твоя задача — вдохновить ученика продолжать, даже если ему было трудно."
                )},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.exception("Ошибка генерации фидбека: %s", e)
        return "Ты отлично справился с заданием. Продолжай в том же духе! 💪"
    
def generate_motivation(name: str, mood: dict, total_completed: int) -> str:
    try:
        mood_summary = (
            f"стресс: {mood.get('score_stress', 'нет данных')}, "
            f"тревожность: {mood.get('score_anxiety', 'нет данных')}, "
            f"позитив: {mood.get('score_positive', 'нет данных')}, "
            f"энергия: {mood.get('score_energy', 'нет данных')}"
        )

        prompt = (
            f"Имя: {name}\n"
            f"Настроение: {mood_summary}\n"
            f"Заданий выполнено: {total_completed}\n\n"
            "Сгенерируй короткое (3–6 предложений) мотивационное сообщение от ИИ-наставника.\n"
            "Учитывай эмоциональное состояние и прогресс. Постарайся вдохновить и поддержать пользователя."
        )

        client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": (
                    "Ты — заботливый ИИ-ментор. Поддерживай, вдохновляй, помогай не сдаваться."
                )},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.exception("Ошибка генерации мотивации: %s", e)
        return "Ты уже проделал большую работу. Продолжай, и ты обязательно справишься! ✨"
