import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="GitHub Monitor", layout="wide")

st.title("📊 Моніторинг проєктів GitHub")

# === 1. Введення даних користувачем ===
st.sidebar.header("⚙️ Налаштування")
repos_input = st.sidebar.text_area(
    "Введіть список репозиторіїв (формат: owner/repo, по одному в рядок):",
    "torvalds/linux\nmicrosoft/vscode\ntensorflow/tensorflow"
)

token = st.sidebar.text_input("GitHub Access Token (необов’язково)", type="password")

if st.sidebar.button("🔍 Отримати дані"):
    repos = [r.strip() for r in repos_input.split("\n") if r.strip()]
    headers = {"Authorization": f"token {token}"} if token else {}

    all_data = []
    since = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"

    st.info("Збираю дані з GitHub...")

    for repo_name in repos:
        url = f"https://api.github.com/repos/{repo_name}"
        commits_url = f"https://api.github.com/repos/{repo_name}/commits?since={since}"

        repo_data = requests.get(url, headers=headers).json()
        commits_data = requests.get(commits_url, headers=headers).json()

        # Перевірка, чи не перевищено ліміт
        if isinstance(repo_data, dict) and repo_data.get("message") == "API rate limit exceeded":
            st.error("⛔ Перевищено ліміт запитів GitHub API! Використайте токен.")
            st.stop()

        commits_count = len(commits_data) if isinstance(commits_data, list) else 0

        all_data.append({
            "Репозиторій": repo_name,
            "⭐ Зірки": repo_data.get("stargazers_count", 0),
