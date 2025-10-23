from github import Github
import pandas as pd
from datetime import datetime, timedelta

# ====== 1. Авторизація через токен GitHub ======
# Створи токен у GitHub (Settings → Developer settings → Personal access tokens)
ACCESS_TOKEN = "your_github_token_here"
g = Github(ACCESS_TOKEN)

# ====== 2. Список репозиторіїв для аналізу ======
repos = [
    "torvalds/linux",
    "microsoft/vscode",
    "tensorflow/tensorflow"
]

# ====== 3. Збір даних ======
data = []
for repo_name in repos:
    repo = g.get_repo(repo_name)

    stars = repo.stargazers_count
    forks = repo.forks_count
    open_issues = repo.open_issues_count

    since = datetime.now() - timedelta(days=30)
    commits = repo.get_commits(since=since).totalCount
    pulls = repo.get_pulls(state="all").totalCount

    data.append({
        "Repository": repo_name,
        "Stars": stars,
        "Forks": forks,
        "Open Issues": open_issues,
        "Commits (30d)": commits,
        "Pull Requests": pulls
    })

df = pd.DataFrame(data)

# ====== 4. Рейтинг за зірками ======
df = df.sort_values("Stars", ascending=False)
print("\nРейтинг проєктів за кількістю зірок:\n")
print(df[["Repository", "Stars"]])

# ====== 5. Графік активності ======
plt.figure(figsize=(10, 5))
plt.bar(df["Repository"], df["Commits (30d)"], color="skyblue")
plt.title("Активність комітів за останні 30 днів")
plt.ylabel("Кількість комітів")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.show()

# ====== 6. Аналіз динаміки ======
print("\nАналіз динаміки розробки:")
for _, row in df.iterrows():
    print(f"- {row['Repository']}: {row['Commits (30d)']} комітів за 30 днів, "
          f"{row['Pull Requests']} pull requests, "
          f"{row['Open Issues']} відкритих issues.")

