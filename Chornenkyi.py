import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# --- Налаштування сторінки ---
st.set_page_config(page_title="GitHub Monitor", layout="wide")

st.title("📊 Моніторинг проєктів GitHub")

# --- Ввід даних користувачем ---
st.sidebar.header("⚙️ Налаштування")
repos_input = st.sidebar.text_area(
    "Введіть список репозиторіїв (формат: owner/repo, кожен з нового рядка):",
    "torvalds/linux\nmicrosoft/vscode\ntensorflow/tensorflow"
)

token = st.sidebar.text_input("GitHub Access Token (необов’язково)", type="password")

if st.sidebar.button("🔍 Отримати дані"):
    repos = [r.strip() for r in repos_input.split("\n") if r.strip()]
    headers = {"Authorization": f"token {token}"} if token else {}

    all_data = []
    since = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"

    st.info("⏳ Збираю дані з GitHub...")

    for repo_name in repos:
        # --- Основні дані репозиторію ---
        repo_url = f"https://api.github.com/repos/{repo_name}"
        commits_url = f"https://api.github.com/repos/{repo_name}/commits?since={since}"

        repo_resp = requests.get(repo_url, headers=headers)
        repo_data = repo_resp.json()

        commits_resp = requests.get(commits_url, headers=headers)
        commits_data = commits_resp.json()

        # --- Перевірка на ліміт API ---
        if isinstance(repo_data, dict) and repo_data.get("message") == "API rate limit exceeded":
            st.error("⛔ Перевищено ліміт запитів GitHub API! Використайте токен.")
            st.stop()

        commits_count = len(commits_data) if isinstance(commits_data, list) else 0

        # --- Додавання до списку ---
        all_data.append({
            "Репозиторій": repo_name,
            "⭐ Зірки": repo_data.get("stargazers_count", 0),
            "🍴 Форки": repo_data.get("forks_count", 0),
            "🐞 Відкриті issues": repo_data.get("open_issues_count", 0),
            "💬 Коміти (30 днів)": commits_count
        })

    # --- Формування DataFrame ---
    df = pd.DataFrame(all_data)

    # --- Рейтинг за зірками ---
    df_sorted = df.sort_values("⭐ Зірки", ascending=False).reset_index(drop=True)
    st.subheader("🏆 Рейтинг проєктів за зірками")
    st.dataframe(df_sorted, use_container_width=True)

    # --- Графік активності ---
    st.subheader("📈 Активність комітів за останні 30 днів")
    st.bar_chart(df.set_index("Репозиторій")["💬 Коміти (30 днів)"])

    # --- Аналіз динаміки ---
    st.subheader("🧠 Аналіз динаміки розробки")
    for _, row in df.iterrows():
        st.write(
            f"- **{row['Репозиторій']}**: {row['💬 Коміти (30 днів)']} комітів, "
            f"{row['🐞 Відкриті issues']} issues, {row['⭐ Зірки']} ⭐"
        )
