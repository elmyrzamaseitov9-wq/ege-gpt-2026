import streamlit as st
import httpx
import re

# ←←← ТВОИ КЛЮЧИ
API_KEY   = "AQVN0SFdgaEgntb54gvJV8YgDj0cnU0XN6E6EOdi"
FOLDER_ID = "b1gqph120fbkgpbskb41"
# ←←←

def ask_yandex_gpt(prompt):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {"Authorization": f"Api-Key {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {"temperature": 0.3, "maxTokens": 2500},  # temperature ниже = точнее
        "messages": [{"role": "user", "text": prompt}]
    }
    try:
        r = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        r.raise_for_status()
        return r.json()["result"]["alternatives"][0]["message"]["text"]
    except Exception as e:
        return f"Ошибка YandexGPT: {e}"

# Инициализация
if "task" not in st.session_state:
    st.session_state.task = None
if "generated" not in st.session_state:
    st.session_state.generated = False

st.set_page_config(page_title="ЕГЭ-GPT 2026", page_icon="robot")
st.title("ЕГЭ-GPT по информатике 2026 — ФИПИ-уровень")

num = st.selectbox("Номер задачи:", ["6", "8", "12", "15", "16", "19-21", "23", "24", "25", "27"])

if st.button("Сгенерировать новую задачу"):
    with st.spinner("Генерирую задачу..."):
        prompt = f"""Ты эксперт ФИПИ. Сгенерируй новую задачу №{num} ЕГЭ 2026 (не из банка).

Выведи строго в трёх частях:
### УСЛОВИЕ
[условие]

### ОТВЕТ
[только чистый ответ — число или короткий код, без пояснений]

### РАЗБОР
[подробный разбор]"""

        result = ask_yandex_gpt(prompt)
        
        parts = {"condition": "", "answer": "", "explanation": ""}
        current = None
        for line in result.split("\n"):
            line = line.strip()
            if line.startswith("### УСЛОВИЕ"): current = "condition"
            elif line.startswith("### ОТВЕТ"): current = "answer"
            elif line.startswith("### РАЗБОР"): current = "explanation"
            elif current and line:
                parts[current] += line + "\n"

        st.session_state.task = parts
        st.session_state.generated = True
        st.success("Задача готова!")

if st.session_state.generated:
    st.markdown("### Условие задачи")
    st.markdown(st.session_state.task["condition"])

    st.markdown("---")
    user_solution = st.text_area("Введи ответ (число или код):", height=100)

    if st.button("Проверить решение"):
        if user_solution.strip():
            with st.spinner("Проверяю по критериям ФИПИ..."):
                # ←←← САМЫЙ ЖЁСТКИЙ И ТОЧНЫЙ ПРОМПТ
                check_prompt = f"""Ты эксперт-оценщик ФИПИ ЕГЭ по информатике.

Правильный ответ: {st.session_state.task['answer'].strip()}

Ответ ученика: "{user_solution.strip()}"

Правила оценки:
1. Если ответ ученика — ТОЧНО такое же число/строка, как правильный — 100 баллов.
2. Если отличается пробелами, регистром, лишними символами — 0 баллов.
3. Никаких пояснений не учитывать — только само значение.

Выведи ровно так:

Баллы: 100 или 0

Критерии проверки:
- Совпадение с правильным ответом → 100 баллов
- Любое отклонение (пробелы, буквы, пояснения) → 0 баллов

Замечания: [если 0 — коротко, почему]"""

                feedback = ask_yandex_gpt(check_prompt)

                st.markdown("### Результат проверки ФИПИ")
                st.markdown(feedback)

                with st.expander("Спойлер: правильный ответ и разбор", expanded=False):
                    st.success(f"Правильный ответ:\n{st.session_state.task['answer']}")
                    st.info(st.session_state.task['explanation'])
        else:
            st.warning("Введи ответ!")
else:
    st.info("↑ Сначала сгенерируй задачу")

st.caption("YandexGPT • Жёсткая проверка как на реальном ЕГЭ • 2026")
