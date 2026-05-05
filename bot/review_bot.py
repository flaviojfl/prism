import os
import time
import requests

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GH_TOKEN = os.environ["GH_TOKEN"]
PR_NUMBER = os.environ["PR_NUMBER"]
REPO_NAME = os.environ["REPO_NAME"]

GITHUB_API = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github+json",
}


def get_pr_diff():
    url = f"{GITHUB_API}/repos/{REPO_NAME}/pulls/{PR_NUMBER}/files"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    files = response.json()

    diff_text = ""
    for file in files:
        filename = file["filename"]
        patch = file.get("patch", "")
        if patch:
            diff_text += f"\n### {filename}\n```\n{patch}\n```\n"

    return diff_text


def review_with_groq(diff):
    prompt = f"""Você é um engenheiro de software sênior revisando um Pull Request.

Analise o diff abaixo e forneça um review construtivo em português.

Seu review deve cobrir:
- Problemas de lógica ou bugs potenciais
- Qualidade e legibilidade do código
- Boas práticas e padrões
- Sugestões de melhoria

Seja direto e construtivo. Se o código estiver bom, diga isso também.

---

{diff}
"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }

    for attempt in range(3):
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 429:
            wait = 30 * (attempt + 1)
            print(f"Rate limited. Esperando {wait}s...")
            time.sleep(wait)
            continue
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    raise Exception("Groq API indisponível após 3 tentativas.")


def post_comment(review):
    url = f"{GITHUB_API}/repos/{REPO_NAME}/issues/{PR_NUMBER}/comments"
    body = f"## 🔍 PRism Review\n\n{review}"
    response = requests.post(url, headers=HEADERS, json={"body": body})
    response.raise_for_status()
    print("Review postado com sucesso.")


def main():
    print("Buscando diff da PR...")
    diff = get_pr_diff()

    if not diff:
        print("Nenhuma alteração encontrada.")
        return

    print("Enviando para o Groq...")
    review = review_with_groq(diff)

    print("Postando comentário na PR...")
    post_comment(review)


if __name__ == "__main__":
    main()