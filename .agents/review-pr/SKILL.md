---
name: review-pr
description: Revisão realista de PR(s) — lê o código de verdade (não só o diff), builda e testa localmente puxando a branch numa cópia isolada, e aponta só problemas com fundamento concreto. Use quando o usuário colar um ou mais links de PR (do mesmo repositório ou de repositórios diferentes ligados por uma mesma feature) e pedir revisão, review, "dá uma olhada nessa PR", "review this PR" ou similar.
metadata:
  version: "2.0"
---

# Revisar PR(s)

## Objetivo

Substituir o "aprovar sem ler" por uma revisão que efetivamente leu o código, rodou build e
testes quando deu, e só aponta o que tem fundamento concreto: sem caçar piolho, sem repetir o
diff em prosa, sem inflar gravidade. Pouco texto, foco no que importa, nada que quem lê já sabe.

## Entrada esperada

Um ou mais URLs de PR, ex.:

```
https://github.com/<owner>/<repo>/pull/<n>
```

Podem ser de repositórios diferentes (comum quando uma feature atravessa um repositório de
contratos ou biblioteca compartilhada e os serviços que a consomem). Não pressuponha que são do
mesmo autor ou repositório.

Os comandos abaixo assumem GitHub com a CLI `gh`. Em outra forja (GitLab com `glab`, por
exemplo), o fluxo é o mesmo: troque os comandos pelos equivalentes da CLI disponível.

## Fluxo

### 1. Metadados de cada PR

```bash
gh pr view <n> --repo <owner>/<repo> --json title,body,headRefName,baseRefName,files,additions,deletions,author,url
```

### 2. Detectar PRs relacionadas

Leia o `body` procurando links para outras PRs ("Depende de", "Relacionado", "Base:" etc.). Se a
PR pedida depende de outra ainda não mergeada (tipicamente uma de contrato, schema ou biblioteca
compartilhada), isso importa: sem o código dela, build e leitura ficam incompletos ou até
enganosos. Avise o usuário que há uma PR relacionada e, se for razoável (poucas PRs, mesma
feature), inclua-a na revisão: não precisa perguntar, só avisar o que está fazendo. Não saia
caçando relacionadas além do que está explícito no body.

### 3. Preparar o código para leitura real (nunca revisar só o diff isolado)

Para cada repositório envolvido:

- **Procure uma cópia local.** Olhe o diretório de trabalho atual e seus vizinhos; se o usuário
  costuma manter os repositórios num diretório conhecido, procure lá. Cuidado com nomes parecidos
  que são repositórios diferentes: confirme pelo remote (`git remote -v`) antes de assumir.
- **Se existir localmente:** `git -C <repo> fetch origin <headRefName> <baseRefName>`. Fetch é
  seguro, não toca na árvore de trabalho. Nunca faça checkout, reset ou clean na cópia de trabalho
  do usuário: pode haver trabalho em andamento.
- **Se não existir:** avise ("não tenho `<repo>` localmente, vou clonar temporariamente") e clone
  num diretório temporário (o scratchpad da sessão, se houver) com `gh repo clone`.
- **Build e testes sempre numa cópia isolada:** `git worktree add` a partir do repositório local
  (removendo ao final com `git worktree remove`), ou o clone temporário.
- **Diff completo, não só a lista de arquivos:** `git diff origin/<base>...origin/<head>`. Leia o
  diff inteiro antes de tirar conclusão, e abra os arquivos tocados para ver o contexto em volta
  de cada trecho alterado.

### 4. Build, lint e testes de verdade, quando der

- **Descubra a interface que o repositório já usa** em vez de inventar comando: instruções para
  agentes (`CLAUDE.md`, `AGENTS.md`), `README`, `CONTRIBUTING`, `Makefile`/`justfile`/`Taskfile`,
  scripts do gerenciador de pacotes. Os workflows de CI (`.github/workflows/`, `.gitlab-ci.yml`
  etc.) são a fonte mais confiável: mostram exatamente o que precisa passar para a PR entrar.
- **Código gerado ou dependência de outra PR.** Se o projeto gera código (de schemas, contratos,
  ORM etc.) e a cópia isolada não tem esse código, rode o passo de geração antes de buildar: é
  setup, não modificação da PR. Se a PR depende de uma PR relacionada não mergeada (passo 2),
  aponte a geração ou a dependência para a branch dela, senão o build falha por falta do que ela
  traz e a revisão vira só leitura estática. Tudo isso só na cópia isolada.
- **Escope** build, lint e testes ao que o diff toca quando o projeto inteiro for caro ou
  instável de rodar.
- **Erro pré-existente não é do autor.** Se algo falha, confirme se já falhava na base antes de
  atribuir à PR.
- **Falha alheia à PR** (credencial, serviço externo, infraestrutura local ausente): registre e
  continue a revisão por leitura de código; não trave a revisão inteira nisso.

### 5. Ler com intenção de achar problema real, nesta ordem de prioridade

1. **Segurança e autorização.** Dado de um usuário, cliente ou tenant vazando para outro;
   identidade e permissão vindas do contexto autenticado, nunca de campo controlado pelo request;
   entrada não validada chegando a query, shell, path ou template; segredo no código ou no log.
2. **Correção de dado.** Lógica de negócio, paginação, cálculo, concorrência, condição de borda
   não coberta por teste.
3. **Contrato.** Interface publicada (API, schema, evento, contrato entre serviços) batendo com a
   implementação; compatibilidade com consumidores existentes; descrição da PR batendo com o diff
   real. Descrição desatualizada costuma esconder trabalho esquecido: confira item por item do
   que ela diz ter feito.
4. **Regressão de proteção.** Limite, validação, timeout ou checagem que existia e sumiu na
   refatoração (ex.: limite fixo virando parametrizado sem teto).
5. **Convenções do projeto.** O que estiver documentado (`CLAUDE.md`, `AGENTS.md`,
   `CONTRIBUTING`, guias do time, configuração de linter) e o que o próprio repositório pratica
   de forma consistente: migrations, variáveis de ambiente documentadas, configuração de
   roteamento ou deploy atualizada quando a mudança exige, branch base correta.
6. **Boas práticas da linguagem e performance.** Idiomas da linguagem e melhorias de performance,
   quando não exigirem refatoração grande para serem contemplados.

**Não aponte:** nomenclatura, formatação, preferência de estilo, "poderia ser mais DRY" quando não
há repetição real de lógica de negócio, nem nada que já é assim no resto do repositório (convenção
local existente vale mais que preferência genérica).

### 6. Reportar no chat primeiro, nunca postar direto

Resuma por PR: o que foi verificado de fato (build, lint, testes rodados, não só leitura) e os
achados com fundamento (`arquivo:linha` ou nome de função, cenário concreto de falha: dado X,
acontece Y, deveria Z). Sem inflar gravidade; se não achou nada, diga isso claramente em vez de
forçar um achado.

**Espere confirmação do usuário antes de postar qualquer coisa na PR.** Comentários saem sob a
conta dele (`gh auth status` mostra qual) e são visíveis a terceiros.

### 7. Postar (só depois do OK)

Um comentário por PR, com o corpo num arquivo temporário (`--body` inline costuma estragar acento,
quebra de linha e crase no shell):

```bash
gh pr comment <n> --repo <owner>/<repo> --body-file <arquivo>
```

- Primeira linha: o que foi verificado de fato (ex.: "build, lint e testes passando localmente com
  a branch da PR"), para distinguir de um LGTM vazio.
- Achados como pergunta ao autor, não veredito ("vale confirmar que...", "foi decisão consciente
  ...?"): o objetivo é abrir discussão, não bloquear.
- PR sem achados: comentário curto confirmando o que foi checado. Não inventar problema só para
  ter o que dizer.
- Direto, sem emoji, no idioma do projeto (ou no da conversa com o usuário, se o projeto não
  definir).
- O comentário sai sob a conta do usuário e se lê como a revisão dele: não acrescente assinatura
  de ferramenta por conta própria. Se o projeto ou o usuário exigir que revisões assistidas sejam
  identificadas, siga essa regra.

## Fora de escopo

- Nunca aprovar ou pedir mudanças formalmente (`gh pr review --approve` / `--request-changes`): a
  decisão é do usuário; a skill só comenta.
- Nunca push ou commit nos repositórios revisados.
- Nunca merge.
