from src.shared.core.settings import settings
from openai import OpenAI
import json
from src.shared.utils.compressor import compress_context

folder_id  = settings.OPEN_AI_FOLDER
api_key = settings.OPEN_AI_KEY

model = f"gpt://{folder_id}/{settings.OPEN_AI_MODEL}"

client = OpenAI(
base_url="https://rest-assistant.api.cloud.yandex.net/v1", api_key=api_key, project=folder_id)

def analyze_comparison_with_gpt(context: dict) -> dict:
    compressed_context = compress_context(context, max_chars=200)

    prompt = f"""
    Ты — UX-аналитик. Сравни поведение пользователей между двумя версиями сайта priem.mai.ru: v1 и v2.
    
    Данные:
    {compressed_context}
    
    Ответь на вопросы:
    - Что улучшилось?
    - Что ухудшилось?
    - Что не изменилось, но ожидалось?
    - Какие сегменты (устройства, браузеры, ОС) показали наибольшее изменение?
    - Какие рекомендации можно дать командам (frontend, UX, mobile)?
    
    Ответь в формате JSON:
    {{
      "summary": "Краткое резюме изменений",
      "improvements": [
        {{
          "metric": "bounce_rate",
          "change": "-5%",
          "affected_segments": ["mobile | ios15"],
          "description": "Описание улучшения"
        }}
      ],
      "regressions": [
        {{
          "metric": "form_submit_rate",
          "change": "-12%",
          "affected_segments": ["desktop | Chrome"],
          "description": "Описание ухудшения"
        }}
      ],
      "expected_no_change": [
        {{
          "metric": "page_views_avg",
          "v1": 1.8,
          "v2": 1.8,
          "expected": "Должно было улучшиться",
          "description": "Описание"
        }}
      ],
      "recommendations": [
        "Рекомендация 1",
        "Рекомендация 2"
      ]
    }}
        """
    print(prompt)
    completion = client.responses.create(
        instructions = "Ты — UX-аналитик. Отвечай структурированно, на русском языке, в формате JSON.",
        input = prompt,
        temperature=0.2,
        model = model
    )

    answer_text = completion.output_text
    print(completion.__repr__())
    try:
        print(answer_text)
        return json.loads(answer_text)
    except json.JSONDecodeError:
        return {"raw_response": answer_text}

if __name__ == "__main__":
    print(analyze_comparison_with_gpt({"v1": {"coolness": 1}, "v2": {"coolness": 2}}))