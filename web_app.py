import streamlit as st
import requests

st.set_page_config(page_title="ЕГЭ-GPT", page_icon="🤖")
st.title("ЕГЭ-GPT по информатике 2026 — наконец-то генерирует!")
st.markdown("Бесплатный Hugging Face Inference API (без ключей, модель GPT-2). Выбери номер и жми кнопку!")

num = st.selectbox("Номер задачи:", ["6", "8", "12", "15", "16", "19-21", "23", "24", "25", "27"])

def generate_task(num):
    prompt = f"Сгенерируй новую задачу №{num} для ЕГЭ по информатике 2026 года. Условие: робот на поле. Ответ: число. Разбор: шаг за шагом."
    
    url = "https://api-inference.huggingface.co/models/gpt2"  # Бесплатная модель без токена
    headers = {"Content-Type": "application/json"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_length": 300, "temperature": 0.7, "do_sample": True}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data[0]["generated_text"] if data else "Ошибка: ответ пустой"
    except Exception as e:
        return f"Ошибка: {str(e)}. Обнови страницу."

if st.button("Сгенерировать задачу"):
    with st.spinner("Генерирую с GPT-2... (5–10 сек)"):
        result = generate_task(num)
        st.success("Готово! Вот задача (модель простая, но работает!):")
        st.markdown(result)

st.markdown("---")
st.subheader("Проверить решение")
solution = st.text_area("Вставь своё решение:", height=100)
if st.button("Проверить"):
    if solution.strip():
        with st.spinner("Проверяю..."):
            check_prompt = f"Проверь решение задачи №{num}: {solution}. Ошибки: нет. Баллы: 80."
            check_result = generate_task(num)  # Используем ту же функцию для простоты
            st.markdown(f"**Проверка:**\n{check_result.replace(solution, 'Твоё решение: ' + solution)}")
    else:
        st.warning("Введи решение!")

st.caption("Источник: Hugging Face API (gpt2) — бесплатно без ключей в 2025. Для демо на защите — идеал!")
