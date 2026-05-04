import os
import requests

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
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


def review_with_gemini(diff):
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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


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

    print("Enviando para o Gemini...")
    review = review_with_gemini(diff)

    print("Postando comentário na PR...")
    post_comment(review)


if __name__ == "__main__":
    main()