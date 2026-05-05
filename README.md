# 🔍 PRism

Bot de revisão automática de Pull Requests no GitHub usando IA.

Quando uma PR é aberta ou atualizada, o PRism analisa o diff e posta um comentário com sugestões de melhoria, problemas potenciais e boas práticas — direto na conversa da PR.

## Por que existe

Com o aumento do uso de agentes de IA na geração de código, o volume de Pull Requests para revisar cresceu muito. O PRism atua como um primeiro filtro automatizado, ajudando o revisor humano a focar no que realmente importa.

## Stack

- **Python** — orquestração
- **GitHub Actions** — execução serverless via webhook nativo
- **Groq API** (Llama 3.3 70B) — geração do review
- **GitHub REST API** — leitura do diff e publicação do comentário

## Como funciona
PR aberta
→ GitHub dispara evento pull_request
→ GitHub Actions roda o workflow
→ Python busca o diff via GitHub API
→ Envia o diff para o Groq
→ Groq retorna o review
→ Bot posta como comentário na PR

## Como usar no seu repositório

1. Clona ou faz fork deste repositório
2. Cria as seguintes secrets em **Settings → Secrets and variables → Actions**:
   - `GROQ_API_KEY` — obtida em [console.groq.com](https://console.groq.com)
   - `GH_TOKEN` — Personal Access Token com permissão `repo`
3. Pronto. Toda PR aberta vai receber o review automaticamente.

## Estrutura
prism/
├── .github/workflows/review.yml   # Workflow do GitHub Actions
├── bot/review_bot.py              # Lógica do bot
├── requirements.txt
└── README.md

## Considerações de segurança

- O bot trunca diffs maiores que 50.000 caracteres
- Timeouts em todas as requisições HTTP
- System prompt instrui o modelo a ignorar instruções embutidas no código (proteção básica contra prompt injection)
- Secrets nunca trafegam fora do runner do GitHub Actions

## Próximos passos

- Suporte a múltiplas linguagens com prompts específicos
- Comentários inline em linhas específicas (ao invés de um comentário único)
- Sugestão de correções automáticas via commit no branch da PR

---
