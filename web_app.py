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
        "completionOptions": {"temperature": 0.0, "maxTokens": 3000},
        "messages": [{"role": "user", "text": prompt}]
    }
    try:
        r = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        r.raise_for_status()
        return r.json()["result"]["alternatives"][0]["message"]["text"]
    except Exception as e:
        return "Ошибка YandexGPT"

if "task" not in st.session_state:
    st.session_state.task = {"condition": "", "answer": "", "explanation": ""}
if "generated" not in st.session_state:
    st.session_state.generated = False

st.set_page_config(page_title="ЕГЭ-GPT 2026", page_icon="robot")
st.title("ЕГЭ-GPT 2026 — ЧИСТЫЙ ТРЕНАЖЁР")

num = st.selectbox("Номер задачи:", ["6", "8", "12", "15", "16", "19-21", "23", "24", "25", "27"])

if st.button("Сгенерировать задачу"):
    with st.spinner("Генерирую..."):
        prompt = f"""Генерируй задачу №{num} ЕГЭ 2026.

### УСЛОВИЕ
[условие]

### ОТВЕТ
[ТОЧНЫЙ ответ без пояснений: число, Да/Нет, ВВНИС, шаблон и т.д.]

### РАЗБОР
[разбор]"""

        result = ask_yandex_gpt(prompt)

        cond = re.search(r"### УСЛОВИЕ\s*(.*?)\s*### ОТВЕТ", result, re.DOTALL)
        ans  = re.search(r"### ОТВЕТ\s*(.*?)\s*### РАЗБОР", result, re.DOTALL)
        expl = re.search(r"### РАЗБОР\s*(.*)", result, re.DOTALL)

        condition = cond.group(1).strip() if cond else "Нет условия"
        raw_answer = ans.group(1).strip() if ans else "42"
        explanation = expl.group(1).strip() if expl else "Нет разбора"

        clean_answer = raw_answer.strip(' "\'[]\\n\\r')

        # Если опять "[число]" — берём из разбора
        if "число" in clean_answer.lower() or not clean_answer:
            numbers = re.findall(r'\d+', explanation)
            clean_answer = " ".join(numbers[:2]) if numbers else "42"

        st.session_state.task = {
            "condition": condition,
            "answer": clean_answer,
            "explanation": explanation
        }
        st.session_state.generated = True
        # ←←← УБРАЛ ВСЁ, ГДЕ МОГ БЫТЬ СПОЙЛЕР!
        st.success("Задача готова! Удачи!")

if st.session_state.generated:
    st.markdown("### Условие")
    st.markdown(st.session_state.task["condition"])

    st.markdown("---")
    user_solution = st.text_area("Твой ответ:", height=120, placeholder="Введи точно как в ЕГЭ")

    if st.button("Проверить"):
        if user_solution.strip():
            user = user_solution.strip()
            correct = st.session_state.task["answer"]

            if user == correct:
                st.balloons()
                st.success("**100/100** — БРАВО!")
            else:
                st.error(f"**0/100**\n\nТвой ответ: `{user}`\nПравильный ответ: `{correct}`")

            with st.expander("Спойлер: ответ + полный разбор"):
                st.success(f"Правильный ответ: `{correct}`")
                st.info(st.session_state.task["explanation"])
        else:
            st.warning("Введи ответ")
else:
    st.info("↑ Выбери номер и нажми кнопку")

st.caption("Никаких спойлеров до проверки • Все типы ответов • ЕГЭ 2026")
