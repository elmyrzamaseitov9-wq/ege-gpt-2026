import streamlit as st
import httpx
import json

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# СЮДА ВСТАВЬ СВОЙ КЛЮЧ YANDEXGPT !!!
API_KEY = "y0_AgAAAAAxxxxxxxxxxxxxxxxxxxxxxxx"   # ← твой ключ сюда
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

def ask_yandex_gpt(prompt):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": "gpt://b1g8v37t8g8s8v8s8v8s/yandexgpt-lite",
        "completionOptions": {"temperature": 0.4, "maxTokens": 2000},
        "messages": [{"role": "user", "text": prompt}]
    }
    response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
    return response.json()["result"]["alternatives"][0]["message"]["text"]

st.set_page_config(page_title="ЕГЭ-GPT", page_icon="")
st.title("ЕГЭ-GPT по информатике 2026")
st.markdown("Генератор задач №6, 8, 12, 15, 16, 19–21, 23, 24, 25, 27")

num = st.selectbox("Номер задачи:", ["6", "8", "12", "15", "16", "19-21", "23", "24", "25", "27"])

if st.button("Сгенерировать задачу"):
    with st.spinner("ИИ генерирует..."):
        prompt = f"""Ты эксперт ФИПИ ЕГЭ по информатике 2026.
        Сгенерируй СОВЕРШЕННО НОВУЮ задачу №{num} (не из банка ФИПИ).
        Формат ответа:
        1. Условие задачи
        2. Правильный ответ
        3. Подробный разбор решения"""
        result = ask_yandex_gpt(prompt)
        st.success("Готово!")
        st.markdown(result)

st.markdown("---")
st.subheader("Проверка решения")
solution = st.text_area("Вставь сюда своё решение:")
if st.button("Проверить"):
    if solution:
        with st.spinner("Проверяю..."):
            check = f"Проверь решение задачи №{num}:\n{solution}\nУкажи ошибки и сколько баллов дал бы эксперт ФИПИ."
            answer = ask_yandex_gpt(check)
            st.markdown(answer)
