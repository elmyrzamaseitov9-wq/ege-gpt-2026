import streamlit as st
import httpx

# ←←← Твои ключи (оставь как есть)
API_KEY   = "AQVN0SFdgaEgntb54gvJV8YgDj0cnU0XN6E6EOdi"
FOLDER_ID = "b1gqph120fbkgpbskb41"
# ←←←

def ask_yandex_gpt(prompt):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {"Authorization": f"Api-Key {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {"temperature": 0.6, "maxTokens": 2500},
        "messages": [{"role": "user", "text": prompt}]
    }
    try:
        r = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        r.raise_for_status()
        return r.json()["result"]["alternatives"][0]["message"]["text"]
    except Exception as e:
        return f"Ошибка: {e}"

st.set_page_config(page_title="ЕГЭ-GPT 2026", page_icon="robot")
st.title("ЕГЭ-GPT по информатике 2026 — финальная версия!")

# ←←← Инициализация сессии один раз
if "task" not in st.session_state:
    st.session_state.task = None
if "generated" not in st.session_state:
    st.session_state.generated = False

num = st.selectbox("Номер задачи:", ["6", "8", "12", "15", "16", "19-21", "23", "24", "25", "27"])

# Генерация задачи
if st.button("Сгенерировать новую задачу"):
    with st.spinner("YandexGPT генерирует задачу..."):
        prompt = f"""Ты эксперт ФИПИ ЕГЭ по информатике 2026.
Сгенерируй новую задачу №{num} (не из банка).

Выведи строго в трёх частях:
### УСЛОВИЕ
[условие]

### ОТВЕТ
[правильный ответ]

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

# Показываем условие (всегда, если сгенерировано)
if st.session_state.generated:
    st.markdown("### Условие задачи")
    st.markdown(st.session_state.task["condition"])

    st.markdown("---")
    st.markdown("### Твоё решение")
    # ←←← БЕЗ key= — теперь не сбрасывает!
    user_solution = st.text_area("Введи сюда решение или ответ:", height=150)

    if st.button("Проверить решение"):
        if user_solution.strip():
            with st.spinner("Проверяю..."):
                check_prompt = f"""Задача №{num}:
{st.session_state.task['condition']}

Решение ученика:
{user_solution}

Ты эксперт ФИПИ. Дай:
- баллы (из 100)
- ошибки
- правильный ответ
- краткий разбор"""
                feedback = ask_yandex_gpt(check_prompt)
                st.markdown("### Результат проверки")
                st.markdown(feedback)

                with st.expander("Спойлер: правильный ответ и разбор", expanded=False):
                    st.success(f"Правильный ответ:\n{st.session_state.task['answer']}")
                    st.info(st.session_state.task['explanation'])
        else:
            st.warning("Напиши хоть что-нибудь :)")
else:
    st.info("↑ Сначала сгенерируй задачу")

st.caption("Работает на YandexGPT • 2026 • Ты — бог информатики!")
