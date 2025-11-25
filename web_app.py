import streamlit as st
import httpx
import re

# ←←← ТВОИ КЛЮЧИ (не трогай)
API_KEY   = "AQVN0SFdgaEgntb54gvJV8YgDj0cnU0XN6E6EOdi"
FOLDER_ID = "b1gqph120fbkgpbskb41"
# ←←←

def ask_yandex_gpt(prompt):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {"Authorization": f"Api-Key {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {"temperature": 0.0, "maxTokens": 3000},
        "messages": [{"role": "user", "text": prompt}]
    }
    try:
        r = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        r.raise_for_status()
        return r.json()["result"]["alternatives"][0]["message"]["text"]
    except Exception as e:
        return "Ошибка YandexGPT"

# Сессия
if "task" not in st.session_state:
    st.session_state.task = {"condition": "", "answer": "", "explanation": ""}
if "generated" not in st.session_state:
    st.session_state.generated = False

st.set_page_config(page_title="ЕГЭ-GPT 2026", page_icon="robot")
st.title("ЕГЭ-GPT 2026 — работает со всеми типами ответов")

num = st.selectbox("Номер задачи:", ["6", "8", "12", "15", "16", "19-21", "23", "24", "25", "27"])

if st.button("Сгенерировать задачу"):
    with st.spinner("Генерирую..."):
        prompt = f"""СТРОГО ВЫПОЛНЯЙ!

Генерируй ТОЛЬКО задачу №{num} ЕГЭ по информатике 2026.

ФОРМАТ ОБЯЗАТЕЛЬНЫЙ:

### УСЛОВИЕ
[текст условия]

### ОТВЕТ
[ТОЧНЫЙ правильный ответ на задачу №{num}. Может быть: число, числа через пробел, «Да»/«Нет», последовательность команд (ВВНИС), шаблон (*? и т.д.), код на Python — всё, что требуется в реальном ЕГЭ. НИКАКИХ ПОЯСНЕНИЙ!]

### РАЗБОР
[подробный разбор]"""

        result = ask_yandex_gpt(prompt)

        # Парсинг
        cond = re.search(r"### УСЛОВИЕ\s*(.*?)\s*### ОТВЕТ", result, re.DOTALL)
        ans  = re.search(r"### ОТВЕТ\s*(.*?)\s*### РАЗБОР", result, re.DOTALL)
        expl = re.search(r"### РАЗБОР\s*(.*)", result, re.DOTALL)

        condition = cond.group(1).strip() if cond else "Нет условия"
        raw_answer = ans.group(1).strip() if ans else "42"
        explanation = expl.group(1).strip() if expl else "Нет разбора"

        # Убираем только лишние кавычки и переносы в начале/конце — больше ничего не трогаем!
        clean_answer = raw_answer.strip(' "\'\\n\\r')

        st.session_state.task = {
            "condition": condition,
            "answer": clean_answer,
            "explanation": explanation
        }
        st.session_state.generated = True
        st.success(f"Задача №{num} готова!")

if st.session_state.generated:
    st.markdown("### Условие")
    st.markdown(st.session_state.task["condition"])

    st.markdown("---")
    user_solution = st.text_area("Твой ответ:", height=120, placeholder="Введи точно как в ЕГЭ (число, Да/Нет, ВВНИС, шаблон и т.д.)")

    if st.button("Проверить"):
        if user_solution.strip():
            user = user_solution.strip()
            correct = st.session_state.task["answer"]

            if user == correct:
                st.balloons()
                st.success("**100/100** — идеально!")
            else:
                st.error(f"**0/100**\n\nТвой ответ: `{user}`\nПравильный: `{correct}`")

            with st.expander("Спойлер: ответ + разбор"):
                st.success(f"Правильный ответ:\n`{correct}`")
                st.info(st.session_state.task["explanation"])
        else:
            st.warning("Введи ответ")
else:
    st.info("↑ Выбери номер и нажми кнопку")

st.caption("Поддерживает ВСЕ типы ответов ЕГЭ • №19-21, №23, №24, №27 — всё работает • 2026")
