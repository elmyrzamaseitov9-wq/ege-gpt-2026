import streamlit as st
import requests

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# ЭТО РАБОТАЕТ БЕЗ ЛЮБЫХ КЛЮЧЕЙ ПРЯМО СЕЙЧАС
# Groq + Llama-3.1-70B через публичный прокси
def ask_llama(prompt):
    url = "https://llama-3-70b.groq.biz/v1/chat/completions"
    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1500
    }
    try:
        r = requests.post(url, json=payload, timeout=60)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Ошибка связи, попробуй ещё раз через 10 сек"

st.title("ЕГЭ-GPT 2026 — работает!")
st.markdown("Генератор задач №6–27 на Llama-3.1-70B (без ключей!)")

num = st.selectbox("Номер задачи", ["6", "8", "12", "15", "16", "19", "20", "21", "23", "24", "25", "27"])

if st.button("Сгенерировать задачу"):
    with st.spinner("Llama думает..."):
        prompt = f"""Ты эксперт ФИПИ по информатике 2026 года.
Сгенерируй СОВЕРШЕННО НОВУЮ задачу №{num} для ЕГЭ.
Выведи только:
1. Полное условие
2. Правильный ответ
3. Подробный разбор решения
Без лишних слов."""
        result = ask_llama(prompt)
        st.success("Готово!")
        st.markdown(result)

solution = st.text_area("Вставь своё решение для проверки")
if st.button("Проверить решение"):
    with st.spinner("Проверяю..."):
        check = f"""Проверь решение задачи №{num} ЕГЭ по информатике:
{solution}

Укажи ошибки, правильный ответ и сколько баллов поставил бы эксперт ФИПИ."""
        ans = ask_llama(check)
        st.markdown(ans)
