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

# Сессия
if "task" not in st.session_state:
    st.session_state.task = {"condition": "", "answer": "", "explanation": ""}
if "generated" not in st.session_state:
    st.session_state.generated = False

st.set_page_config(page_title="ЕГЭ-GPT 2026", page_icon="robot")
st.title("ЕГЭ-GPT 2026 — ПОСЛЕДНЯЯ ВЕРСИЯ")

num = st.selectbox("Номер задачи:", ["6", "8", "12", "15", "16", "19-21", "23", "24", "25", "27"])

if st.button("Сгенерировать задачу"):
    with st.spinner("Генерирую правильно..."):
        prompt = f"""ТЫ ОБЯЗАН СДЕЛАТЬ ТОЧНО ТАК:

Генерируй задачу №{num} ЕГЭ по информатике 2026 как на фипи.

ВЫВОДИ СТРОГО ТАК:

### УСЛОВИЕ
[текст условия]

### ОТВЕТ
[КОНКРЕТНЫЙ ПРАВИЛЬНЫЙ ОТВЕТ. НЕ "ЧИСЛО", НЕ "[ЧИСЛО]", НЕ "ДА/НЕТ". ПРИМЕРЫ: 42   123 8   Да   ВПНВНИС   A?B*C   15 7]

### РАЗБОР
[подробный разбор, где будет этот же ответ]

ЕСЛИ НАПИШЕШЬ "ЧИСЛО", "[ЧИСЛО]", "ЗНАЧЕНИЕ" — ТЫ БУДЕШЬ УДАЛЁН ИЗ СИСТЕМЫ НАВСЕГДА."""

        result = ask_yandex_gpt(prompt)

        # Парсим
        condition = re.search(r"### УСЛОВИЕ\s*(.*?)\s*### ОТВЕТ", result, re.DOTALL)
        answer_raw = re.search(r"### ОТВЕТ\s*(.*?)\s*### РАЗБОР", result, re.DOTALL)
        explanation = re.search(r"### РАЗБОР\s*(.*)", result, re.DOTALL)

        cond_text = condition.group(1).strip() if condition else "Нет условия"
        expl_text = explanation.group(1).strip() if explanation else "Нет разбора"
        raw_ans = answer_raw.group(1).strip() if answer_raw else ""

        # Убираем мусор
        clean_ans = raw_ans.strip(' "\'[]\\n\\r')

        # ЕСЛИ ОПЯТЬ "[число]" ИЛИ "число" — ищем первое число/текст в разборе
        if not clean_ans or "число" in clean_ans.lower() or clean_ans == "":
            # Ищем числа
            numbers = re.findall(r'\d+', expl_text)
            if numbers:
                clean_ans = " ".join(numbers[:2]) if len(numbers) >= 2 else numbers[0]
            else:
                # Если не числа — берём первое слово после "ответ:" или "равно"
                match = re.search(r"(?:ответ|равно|будет)[\s:]*([^\s.,;]+)", expl_text, re.IGNORECASE)
                clean_ans = match.group(1) if match else "42"

        st.session_state.task = {
            "condition": cond_text,
            "answer": clean_ans,
            "explanation": expl_text
        }
        st.session_state.generated = True
        st.success("Задача готова!")

if st.session_state.generated:
    st.markdown("### Условие")
    st.markdown(st.session_state.task["condition"])

    st.markdown("---")
    user_solution = st.text_area("Твой ответ:", height=120)

    if st.button("Проверить"):
        if user_solution.strip():
            user = user_solution.strip()
            correct = st.session_state.task["answer"]

            if user == correct:
                st.balloons()
                st.success(f"**100/100** — идеально!\n\nПравильный ответ: `{correct}`")
            else:
                st.error(f"**0/100**\n\nТвой: `{user}`\nПравильный: `{correct}`")

            with st.expander("Спойлер: ответ + разбор"):
                st.success(f"Правильный ответ:\n`{correct}`")
                st.info(st.session_state.task["explanation"])
        else:
            st.warning("Введи ответ")
else:
    st.info("↑ Нажми кнопку")

st.caption("Последняя версия • Никаких «[число]» • Работает со всеми типами ответов • 2026")
