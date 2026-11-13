---
name: create-pr
description: Use SEMPRE que a tarefa for abrir pull request — "abre a PR", "sobe a PR", "cria o pull request", "manda pra review", "abre PR dessa branch", "open a PR" — e também quando o trabalho terminou e o próximo passo é publicar a mudança para revisão, mesmo que o pedido original já dissesse "abra a PR" desde o começo. Cobre como descobrir as convenções do repositório (branch base, template, formato de título, idioma, revisores), o formato padrão de título e descrição (o que mudou / por que / como validar) quando o repositório não define o seu, a conferência dos revisores e a ordem de abertura quando a mesma feature atravessa vários repositórios.
---

# Abertura de pull request

Uma PR boa é curta, diz o que entrega, por que, e como conferir, e chega ao revisor certo contra
a base certa. O caminho é sempre o mesmo: primeiro descobrir as convenções que o repositório já
tem e, só na falta delas, aplicar o padrão desta skill. Improvisar título, base ou revisor gera
retrabalho na revisão.

Os comandos assumem GitHub com a CLI `gh`. Em outra forja (GitLab com `glab mr create`, por
exemplo), o fluxo é o mesmo com os comandos equivalentes; sem CLI disponível, entregue título e
descrição prontos para o usuário colar.

## 1. Descobrir as convenções do repositório

Consulte as fontes abaixo. Quando divergirem, a de cima vence:

1. **Instrução explícita do usuário** na conversa.
2. **Instruções do projeto para agentes:** `CLAUDE.md`, `AGENTS.md` ou equivalente, na raiz do
   repositório e nos diretórios acima dele.
3. **Guia de contribuição:** `CONTRIBUTING.md`, `docs/`, ou o que o `README` apontar.
4. **Template de PR:** `.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE/`,
   `docs/pull_request_template.md`. Se existir, **o template manda na descrição**: preencha as
   seções dele em vez dos três blocos da seção 4.
5. **Histórico:** as últimas PRs mergeadas e os commits da base mostram o formato de título, o
   idioma e a base que o time usa de fato.

   ```bash
   gh pr list --state merged --limit 10 --json title,baseRefName
   git log --oneline -20 origin/<base>
   ```

6. **Configuração da forja:** `CODEOWNERS` (em `.github/`, na raiz ou em `docs/`) para revisores;
   a branch padrão para a base.

   ```bash
   gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
   ```

Saia desta etapa sabendo: **branch base, idioma, formato do título, estrutura da descrição,
revisores e política de atribuição.** O que nenhuma fonte responder segue o padrão desta skill.
Se a base ou os revisores ficarem ambíguos (ex.: `develop` e `main` ativos e o histórico
misturado), pergunte ao usuário em vez de chutar: PR contra a base errada é retrabalho para todo
mundo.

## 2. Antes de abrir

Confirme, nesta ordem:

1. **A branch está publicada.** `git push -u origin <branch>` antes de qualquer coisa.
2. **A base é a definida na etapa 1.** Nunca outra feature branch, a menos que o usuário peça
   uma PR empilhada.
3. **A branch está pronta para entrar na base.** Não abra PR de trabalho parcial como se fosse
   final: se algo ficou de fora, termine ou combine com o usuário abrir como rascunho (`--draft`).
4. **Build e testes passam** no escopo tocado, rodados pela interface que o repositório já usa
   (`Makefile`, scripts do gerenciador de pacotes, os comandos do workflow de CI). Se houver
   falha pré-existente sem relação com a mudança, escope aos módulos que você mexeu e **mencione
   a falha pré-existente na descrição** em vez de arrastar a correção para dentro da PR.
5. **Só entra no commit o que é da mudança.** Revise `git status` e `git diff --staged`:
   configuração local, apontamentos temporários para branches de dependência, segredos e
   artefatos gerados que o repositório não versiona ficam de fora.

## 3. Título

Formato do repositório, se houver. Senão, Conventional Commits:

```
<tipo>: <frase curta>
```

Tipos: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `build`, `ci`, `style`.
Minúscula, sem ponto final, no idioma do projeto.

O título sai do **contexto da mudança**, não do arquivo mexido nem do nome da branch. Se a PR
tem vinte arquivos, o título responde "o que isso entrega?" numa frase.

```
feat: permite transferir a titularidade de uma conta para outro cliente
```

## 4. Descrição

Template do repositório, se houver. Senão, três blocos, nesta ordem, **sem mais nada**:

**O que mudou.** O que a PR faz, em itens curtos. Um item por mudança que o revisor precisa
enxergar separadamente.

**Por que.** O motivo da mudança, em uma ou duas frases. É aqui que entra a referência a issue,
ticket ou decisão de produto: a PR é o lugar certo para proveniência. Se o projeto fecha issues
pela PR, use a palavra-chave da forja (`Closes #123`).

**Como validar.** Os comandos e passos que o revisor roda para conferir. Concreto: comando
exato, rota exata, query exata. Se você validou de alguma forma (subiu o serviço, chamou o
endpoint, rodou a migration do zero), diga o que fez e o que deu.

Regras de escrita:

- **Idioma do projeto**; se o projeto não definir, o da conversa com o usuário. Nomes de arquivo,
  função, tipo, comando e rota ficam como estão no código.
- **Objetivo e direto ao ponto.** Sem repetição, sem reafirmar o título, sem parágrafo de
  contexto que o revisor já tem.
- Se uma decisão sua diverge do que a issue, a spec ou o guia pediam, **diga em uma linha** e
  explique o motivo. É a informação mais útil da descrição.
- Não descreva o que a PR **não** faz, nem liste arquivo por arquivo: o revisor tem o diff.

Escreva o corpo num arquivo temporário (o scratchpad da sessão, se houver) e use `--body-file`:
`--body` inline costuma estragar acento, quebra de linha e crase no shell.

## 5. Autoria e atribuição

A PR e os commits saem com a identidade já configurada no `gh` e no `git`: não altere
`gh auth` nem `git config`.

Assinatura de ferramenta ou assistente (rodapé do tipo "Generated with...", trailer
`Co-Authored-By`) segue a política do projeto e do usuário: inclua se pedirem, omita se
proibirem. Sem política definida, siga o padrão do seu ambiente.

## 6. Revisores

Origem, nesta ordem: instrução do usuário, instruções do projeto, `CODEOWNERS`. Se o
`CODEOWNERS` cobre os arquivos, a forja já atribui sozinha: não duplique à mão. Sem nenhuma
dessas fontes, abra sem revisor e diga isso ao usuário. **Nunca escolha revisor por conta
própria** com base em quem commitou por último ou em quem parece dono do código.

```bash
gh pr create \
  --base <base> \
  --title "<título>" \
  --body-file <arquivo> \
  --reviewer <usuario-ou-org/time>   # só se a etapa 1 definiu revisor
```

### Conferir se o revisor entrou

O `gh pr create` não falha quando só o revisor não entra: a PR nasce e o erro passa
despercebido. Acontece, por exemplo, quando o time não é colaborador do repositório
(`422 Reviews may only be requested from collaborators`). Confira depois de criar:

```bash
gh api repos/<owner>/<repo>/pulls/<numero>/requested_reviewers \
  --jq '"usuários=\([.users[].login]|join(",")) | times=\([.teams[].slug]|join(","))"'
```

Se o revisor esperado não aparece, **avise o usuário de forma explícita**, nomeando o
repositório e o número da PR, para ele ajustar. Não substitua por outra pessoa, não mexa em
permissões do repositório, não repita a chamada esperando resultado diferente.

## 7. Várias PRs para a mesma feature

Quando a mudança atravessa repositórios, **a ordem de abertura segue a ordem de dependência**, e
a de merge também:

1. Primeiro o que é compartilhado: contratos (schemas de API, definições de mensagem, eventos),
   bibliotecas internas, migrations de banco compartilhado.
2. Depois os serviços que produzem ou expõem o que mudou.
3. Por último os que consomem.

Cada repositório leva **sua própria** PR, com título e descrição próprios: não replique o mesmo
texto em todas. Na descrição de cada uma, aponte com link completo a PR da qual ela depende.

Se um consumidor só compila apontando para a branch ainda não mergeada da dependência (branch de
git, versão pre-release, override local de dependência), não commite esse apontamento sem
combinar com o usuário. A volta para a versão publicada depois do merge também é decisão dele.

## 8. Depois de abrir

Termine a resposta com a **lista das PRs abertas**, uma URL completa por linha, na ordem de
abertura, sem título, número solto nem texto entre elas, pronta para copiar e colar onde o time
pede revisão:

```
https://github.com/<owner>/<repo-contratos>/pull/42
https://github.com/<owner>/<repo-servico>/pull/118
https://github.com/<owner>/<repo-consumidor>/pull/77
```

Vale também para uma PR só. Avisos (revisor que não entrou, falha pré-existente) vão **fora**
da lista, antes ou depois dela.

## Nunca faça

- Abrir PR contra base diferente da definida na etapa 1.
- Ignorar o template de PR do repositório.
- Escolher revisor por conta própria, ou substituir um que não entrou.
- Commitar configuração local, segredo ou apontamento temporário para branch de dependência.
- Abrir a PR de um consumidor antes da PR de que ela depende.
- Contrariar a política de atribuição do projeto ou do usuário.
- Descrever o que a PR **não** faz, ou listar arquivo por arquivo: o revisor tem o diff.
