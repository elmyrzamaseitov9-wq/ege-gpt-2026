import streamlit as st
import httpx
import time

# ←←← ТВОИ КЛЮЧИ
API_KEY   = "AQVN0SFdgaEgntb54gvJV8YgDj0cnU0XN6E6EOdi"
FOLDER_ID = "b1gqph120fbkgpbskb41"
# ←←←

def ask_yandex_gpt(prompt, retry=3):
    for attempt in range(retry):
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {"Authorization": f"Api-Key {API_KEY}", "Content-Type": "application/json"}
        payload = {
            "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
            "completionOptions": {"temperature": 0.6, "maxTokens": 2500},
            "messages": [{"role": "user", "text": prompt}]
        }
        try:
            st.write(f"Попытка {attempt+1}...")  # Отладка в интерфейсе
            r = httpx.post(url, headers=headers, json=payload, timeout=90.0)  # Увеличил timeout
            r.raise_for_status()
            st.write("Yandex ответил!")  # Отладка
            return r.json()["result"]["alternatives"][0]["message"]["text"]
        except Exception as e:
            st.write(f"Ошибка {attempt+1}: {str(e)}")  # Показываем ошибку
            if attempt < retry - 1:
                time.sleep(2)  # Пауза перед ретраем
            else:
                st.warning("YandexGPT не отвечает — использую шаблон.")
                return "Шаблонная задача: №{num}. Условие: Робот на поле 5x5. Ответ: 70. Разбор: Рекурсия f(x,y) = f(x-1,y) + f(x,y-1)."

# Инициализация
if "task" not in st.session_state:
    st.session_state.task = None
if "generated" not in st.session_state:
    st.session_state.generated = False

st.set_page_config(page_title="ЕГЭ-GPT 2026", page_icon="robot")
st.title("ЕГЭ-GPT по информатике 2026")

num = st.selectbox("Номер задачи:", ["6", "8", "12", "15", "16", "19-21", "23", "24", "25", "27"])

if st.button("Сгенерировать новую задачу"):
    with st.spinner("Генерирую..."):
        prompt = f"""Ты эксперт ФИПИ. Сгенерируй новую задачу №{num}.

### УСЛОВИЕ
[условие]

### ОТВЕТ
[ответ]

### РАЗБОР
[разбор]"""

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
        st.success("Готово!")

if st.session_state.generated:
    st.markdown("### Условие")
    st.markdown(st.session_state.task["condition"])

    st.markdown("---")
    user_solution = st.text_area("Твоё решение:", height=150)

    if st.button("Проверить"):
        if user_solution.strip():
            with st.spinner("Проверяю..."):
                check_prompt = f"""Задача №{num}:
{st.session_state.task['condition']}

Решение: {user_solution}

Правильный ответ: {st.session_state.task['answer'].strip()}

Оцени объективно:
- Баллы: [0-100]
- Вердикт: [верно/почти/неверно]
- Пояснение: [почему]"""

                feedback = ask_yandex_gpt(check_prompt)
                st.markdown("### Проверка")
                st.markdown(feedback)

                with st.expander("Спойлер"):
                    st.success(f"Ответ: {st.session_state.task['answer']}")
                    st.info(st.session_state.task['explanation'])
        else:
            st.warning("Введи решение!")
else:
    st.info("Сгенерируй задачу ↑")

st.caption("YandexGPT • Если не отвечает — шаблон.")
