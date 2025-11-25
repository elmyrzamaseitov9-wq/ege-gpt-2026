
import streamlit as st
import httpx

# ←←← ТВОИ КЛЮЧИ
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
        return f"Ошибка YandexGPT: {e}"

# Инициализация
if "task" not in st.session_state:
    st.session_state.task = None
if "generated" not in st.session_state:
    st.session_state.generated = False

st.set_page_config(page_title="ЕГЭ-GPT 2026", page_icon="robot")
st.title("ЕГЭ-GPT по информатике 2026")

num = st.selectbox("Номер задачи:", ["6", "8", "12", "15", "16", "19-21", "23", "24", "25", "27"])

if st.button("Сгенерировать новую задачу"):
    with st.spinner("YandexGPT думает..."):
        prompt = f"""Ты эксперт ФИПИ ЕГЭ по информатике 2026.
Сгенерируй новую задачу №{num} (не из банка ФИПИ).

Выведи строго в трёх частях:
### УСЛОВИЕ
[условие]

### ОТВЕТ
[правильный ответ — число или короткий код]

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
    user_solution = st.text_area("Твоё решение или ответ:", height=150)

    if st.button("Проверить решение"):
        if user_solution.strip():
            with st.spinner("Проверяю..."):
                check_prompt = f"""Ты объективный и справедливый эксперт ФИПИ ЕГЭ по информатике.

Сначала сделай chain-of-thought:
1. Прочитай условие.
2. Определи правильный ответ: {st.session_state.task['answer'].strip()}
3. Сравни с решением ученика.
4. Если ответ совпадает — дай 100 баллов.
5. Если почти совпадает (разные пробелы, регистр) — 90–100.
6. Если логика верная, но ошибка в вычислении — 70–90.

Задача №{num}:
{st.session_state.task['condition']}

Решение ученика:
{user_solution}

Правильный ответ:
{st.session_state.task['answer'].strip()}

Полный разбор:
{st.session_state.task['explanation'].strip()}

Сравни решение ученика с правильным.
Дай честную оценку:
- Баллы: [0–100]
- Верно ли? (да/нет/почти)
- Ошибки: [если есть]
- Как исправить: [коротко]"""
                
                feedback = ask_yandex_gpt(check_prompt)
                st.markdown("### Результат проверки")
                st.markdown(feedback)

                with st.expander("Спойлер: ответ и разбор", expanded=False):
                    st.success(f"Правильный ответ:\n{st.session_state.task['answer']}")
                    st.info(st.session_state.task['explanation'])
        else:
            st.warning("Введи решение!")
else:
    st.info("↑ Сначала сгенерируй задачу")

st.caption("Работает на YandexGPT • 2026 • Ты — гений!")
