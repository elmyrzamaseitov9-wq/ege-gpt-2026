import streamlit as st
import httpx

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# 1. ВСТАВЬ СВОЙ API-КЛЮЧ СЮДА:
API_KEY = AQVN0SFdgaEgntb54gvJV8YgDj0cnU0XN6E6EOdi   # ← твой ключ
# 2. ВСТАВЬ СВОЙ ID КАТАЛОГА СЮДА (b1g...):
FOLDER_ID = b1gqph120fbkgpbskb41                    # ← твой folder_id
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

def ask_yandex_gpt(prompt):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "temperature": 0.6,
            "maxTokens": 2000
        },
        "messages": [
            {"role": "user", "text": prompt}
        ]
    }
    try:
        r = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        r.raise_for_status()
        return r.json()["result"]["alternatives"][0]["message"]["text"]
    except Exception as e:
        return f"Ошибка YandexGPT: {str(e)}"

st.set_page_config(page_title="ЕГЭ-GPT 2026", page_icon="robot")
st.title("ЕГЭ-GPT по информатике 2026")
st.markdown("Генератор и проверка задач №6–27 на настоящем YandexGPT")

num = st.selectbox("Номер задачи:", ["6", "8", "12", "15", "16", "19-21", "23", "24", "25", "27"])

if st.button("Сгенерировать новую задачу"):
    with st.spinner("YandexGPT думает..."):
        prompt = f"""Ты эксперт ФИПИ ЕГЭ по информатике 2026 года.
Сгенерируй СОВЕРШЕННО НОВУЮ задачу №{num} (не из открытого банка ФИПИ).
Выведи строго в формате:
1. Условие задачи
2. Правильный ответ (число или короткий код)
3. Подробный разбор решения шаг за шагом"""
        result = ask_yandex_gpt(prompt)
        st.success("Готово!")
        st.markdown(result)

st.markdown("---")
st.subheader("Проверка решения")
solution = st.text_area("Вставь сюда своё решение или ответ:")
if st.button("Проверить"):
    if solution.strip():
        with st.spinner("Проверяю..."):
            check = f"""Ты строгий эксперт ЕГЭ. Проверь решение задачи №{num}:
{solution}

Укажи ошибки, правильный ответ и сколько баллов дал бы ФИПИ (из 100)."""
            answer = ask_yandex_gpt(check)
            st.markdown(answer)
    else:
        st.warning("Сначала введи решение!")
