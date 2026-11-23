# Backlog do Ciclo Box

Lista do que o back-end precisa entregar até **07/12**, organizada por fluxo. Cada pessoa pega um fluxo (ou algumas histórias dele) e faz de ponta a ponta: regra, tabela, migration, endpoint e teste.

Responsável pelo front: _a definir_. Ele vai consumir os endpoints descritos aqui, então vale manter os nomes e os formatos combinados. Se precisar mudar, avisa no grupo.

As regras de negócio vieram do protótipo em `frontend/index.html`, que foi só um ponto de partida e não é o front final. Se o grupo quiser mudar alguma regra, muda aqui primeiro.

## Fluxos

| Fluxo | Histórias | Módulo |
|---|---|---|
| Antes de começar | T01, T02, T03 | vários |
| Login e cadastro | HU01, HU02 | `contas` |
| Catálogo | HU03 | `catalogo` |
| Assinar o Clube | HU04, HU05, HU06 | `assinaturas` |
| Gerenciar a assinatura | HU07, HU08, HU09, HU10, HU11 | `assinaturas` |
| Carrinho e pedidos da loja | HU12, HU13, HU14, HU15 | `pedidos` |
| Compra programada | HU16, HU17, HU18 | `pedidos` |
| Pagamentos | HU19 | `pagamentos` |

As histórias marcadas com **(se der tempo)** podem ficar de fora se o prazo apertar.

## Padrões para todos

Para o código ficar com a mesma cara, independente de quem fez:

- **Onde fica cada coisa** (o CI barra se fugir disso):
  - `domain/`: a entidade como classe Python pura (`dataclass`) e as regras. Não pode importar SQLAlchemy nem FastAPI.
  - `application/`: o caso de uso, que busca no repositório, chama a regra e salva.
  - `adapters/`: o model do SQLAlchemy (tabela), o repositório e as rotas do FastAPI.
  - `facade.py`: o que outros módulos podem chamar.
- **Rotas:** todas começam com `/api`. Nomes em português, no plural (`/api/produtos`, `/api/pedidos`).
- **Ações de estado** (pausar, pular, cancelar...) são `POST` em `/<recurso>/<ação>`.
- **Respostas de erro:**
  - `401`: sem login ou token inválido.
  - `404`: não encontrado.
  - `409`: regra de negócio impede a ação (ex.: pular caixa com a assinatura pausada). Corpo: `{"detail": "mensagem para o cliente"}`.
  - `422`: dado inválido (CEP com 7 dígitos, e-mail sem @). O FastAPI já faz isso pelo schema do Pydantic e devolve uma lista em `detail`, com o campo que deu erro em `loc`:
    ```json
    { "detail": [ { "loc": ["body", "cep"], "msg": "String should have at least 8 characters", "type": "string_too_short" } ] }
    ```
- **Valores em dinheiro no JSON:** sempre como texto com duas casas (`"89.90"`), para não perder centavo no caminho.
- **Datas no JSON:** `"2026-12-24"` para data e `"2026-11-30T14:00:00"` para data com hora.
- **Dinheiro:** `Decimal` no Python e `Numeric(10, 2)` no banco. Nunca `float`.
- **Arredondamento:** todo valor calculado (desconto, frete, total) é arredondado para centavos **logo depois de cada conta**, com meio para cima (`0,005` vira `0,01`). O passo seguinte usa o valor já arredondado. Em Python:
  ```python
  from decimal import ROUND_HALF_UP, Decimal

  def arredondar(valor: Decimal) -> Decimal:
      return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
  ```
  Exemplo: 5% de R$ 189,90 = R$ 9,495 → **R$ 9,50**. O desconto de membro é calculado sobre R$ 229,70 − R$ 9,50, e não sobre R$ 229,70 − R$ 9,495.
  A função `arredondar` fica num lugar só, para todos os módulos usarem a mesma (combinar onde no T01).
- **Entre módulos:** guardar só o id (ex.: `usuario_id`), sem chave estrangeira para tabela de outro módulo.
- **Migration:** uma por PR. Antes do merge, atualizar a branch com a `main`; se outra migration entrou antes, regerar a sua.

## Antes de começar

**T01: Modelo de entidades**
- [ ] Desenhar o diagrama com Usuario, Produto, Assinatura, HistoricoAssinatura, Pedido, ItemPedido, CompraProgramada e Pagamento, com os campos principais.
- [ ] Combinar no grupo antes de alguém criar tabela.

**T02: Criar o módulo `pedidos`**
- [ ] Criar `backend/src/ciclobox/pedidos/` com `domain/`, `application/`, `adapters/`, `ports.py` e `facade.py`, igual aos outros.
- [ ] Adicionar o módulo nos contratos do import-linter no `pyproject.toml`.

**T03: Módulo de referência (Produto)**
- [ ] Fazer o Produto completo (entidade, tabela, migration e seed) para servir de exemplo para todo mundo copiar o padrão.
- [ ] Seed com uma lista inicial de produtos. A lista do protótipo (`PRODUCTS` no `frontend/index.html`) serve de ponto de partida, mas o grupo pode mudar à vontade.

Depois do T03 pronto, cada um segue o mesmo caminho.

## Fluxo: Login e cadastro

### HU01: Cadastro de cliente

> Como cliente, quero criar uma conta para acompanhar meus pedidos e minha assinatura.

**Endpoint:** `POST /api/contas`

```json
// requisição
{ "nome": "Ana Souza", "email": "ana@email.com", "senha": "minhasenha123" }

// resposta 201
{ "id": 1, "nome": "Ana Souza", "email": "ana@email.com" }
```

**Regras:**
- Nome obrigatório.
- E-mail em formato válido (senão `422`) e único (senão `409`).
- Senha com pelo menos 8 caracteres, guardada com hash, nunca em texto puro.

**Tarefas:**
- [ ] Entidade `Usuario` no `domain/`.
- [ ] Tabela `usuarios` (id, nome, email único, senha_hash, criado_em) e migration.
- [ ] Repositório com `salvar` e `buscar_por_email`.
- [ ] Caso de uso `cadastrar_usuario`.
- [ ] Rota e schemas Pydantic de entrada e saída. A resposta nunca devolve a senha.
- [ ] Testes: cadastro ok, e-mail repetido, e-mail inválido.

### HU02: Login

> Como cliente, quero entrar na minha conta para acessar "Minha conta".

**Endpoints:**

`POST /api/contas/login`

```json
// requisição
{ "email": "ana@email.com", "senha": "minhasenha123" }

// resposta 200
{ "access_token": "eyJhbGciOi...", "token_type": "bearer" }
```

`GET /api/contas/eu`: devolve o usuário logado. Precisa do header `Authorization: Bearer <token>`.

```json
// resposta 200
{ "id": 1, "nome": "Ana Souza", "email": "ana@email.com" }
```

**Regras:**
- E-mail ou senha errados: `401`, com a mesma mensagem nos dois casos (não dizer qual está errado).

**Tarefas:**
- [ ] Escolher as libs de token (JWT) e de hash de senha e avisar o grupo antes de adicionar no `pyproject.toml`.
- [ ] Caso de uso `autenticar`.
- [ ] Dependência do FastAPI `usuario_logado` que lê o token e devolve o usuário. **Todo mundo vai usar** nas rotas de "Minha conta", então é bom sair cedo.
- [ ] Rotas de login e `/eu`.
- [ ] Testes: login ok, senha errada, rota protegida sem token.

## Fluxo: Catálogo

### HU03: Listar produtos com filtros

> Como cliente, quero filtrar os produtos por pet e categoria para achar o que preciso.

**Endpoints:**

`GET /api/produtos?pet=cao&categoria=Petiscos` (os dois filtros são opcionais)

```json
// resposta 200
[
  {
    "id": 1,
    "nome": "Ração Premium Cães Adultos 10kg",
    "pet": "cao",
    "categoria": "Alimentação",
    "preco": "189.90",
    "aceita_programada": true
  }
]
```

`GET /api/produtos/{id}`

```json
// resposta 200
{
  "id": 1,
  "nome": "Ração Premium Cães Adultos 10kg",
  "pet": "cao",
  "categoria": "Alimentação",
  "preco": "189.90",
  "aceita_programada": true
}

// resposta 404
{ "detail": "Produto não encontrado" }
```

**Regras:**
- `pet` aceita `cao` ou `gato`. Sem o filtro, vem tudo.
- Produtos com `pet = "ambos"` aparecem tanto no filtro de cão quanto no de gato.
- `categoria` aceita: Alimentação, Petiscos, Brinquedos, Higiene, Acessórios.

**Tarefas:**
- [ ] Usar a entidade e a tabela do T03.
- [ ] Repositório com `listar(pet, categoria)` e `buscar_por_id`.
- [ ] Regra do filtro "ambos" no `domain/` ou na consulta.
- [ ] Rotas.
- [ ] `facade.py` com `buscar_produtos(ids)`, que o fluxo de pedidos vai usar para pegar preço e se aceita programada.
- [ ] Testes: filtro por cão traz "ambos", filtro por categoria, produto inexistente.

## Fluxo: Assinar o Clube

### HU04: Listar planos

> Como cliente, quero ver os planos do Clube para escolher o que cabe no meu bolso.

**Endpoint:** `GET /api/planos`

```json
// resposta 200
[
  { "codigo": "mensal", "nome": "Mensal", "preco_caixa": "89.90", "caixas_por_cobranca": 1, "frete_gratis": false },
  { "codigo": "trimestral", "nome": "Trimestral", "preco_caixa": "79.90", "caixas_por_cobranca": 3, "frete_gratis": false },
  { "codigo": "anual", "nome": "Anual", "preco_caixa": "69.90", "caixas_por_cobranca": 12, "frete_gratis": true }
]
```

**Tarefas:**
- [ ] Planos como constante no `domain/` (não precisa de tabela, são fixos).
- [ ] Rota.

### HU05: Calcular o preço da assinatura

> Como cliente, quero ver o valor final antes de assinar.

**Endpoint:** `POST /api/assinaturas/simulacao`

```json
// requisição
{ "pet": "cao", "porte": "medio", "plano": "trimestral", "cupom": "PRIMEIRA10" }

// resposta 200
{
  "valor_por_caixa": "84.90",
  "caixas_por_cobranca": 3,
  "subtotal": "254.70",
  "frete": "29.70",
  "desconto_cupom": "8.49",
  "total": "275.91"
}
```

**Regras:**
- `valor_por_caixa` = preço do plano + adicional de porte. Adicional só para cão: pequeno R$ 0, médio R$ 5, grande R$ 10.
- `subtotal` = `valor_por_caixa` × `caixas_por_cobranca`.
- `frete` = R$ 9,90 × `caixas_por_cobranca`. No anual é R$ 0.
- `desconto_cupom`: com `PRIMEIRA10`, 10% de **uma** caixa (`valor_por_caixa` × 0,10).
- `total` = `subtotal` − `desconto_cupom` + `frete`.
- `porte` é obrigatório para cão e ignorado para gato.
- Cupom inexistente: `422` com "Cupom não encontrado".

**Tarefas:**
- [ ] Função de cálculo no `domain/`, sem banco. É a parte mais fácil de testar, então caprichar nos testes.
- [ ] Rota.
- [ ] Testes: cada plano, cada porte, gato sem porte, com e sem cupom, frete do anual.

### HU06: Assinar o Clube

> Como cliente, quero assinar o Clube para receber uma caixa surpresa todo mês.

**Endpoints:**

`POST /api/assinaturas` (precisa de login)

```json
// requisição
{
  "pet": "cao",
  "porte": "medio",
  "plano": "trimestral",
  "cupom": "PRIMEIRA10",
  "nome": "Ana Souza",
  "email": "ana@email.com",
  "cep": "37500000",
  "pagamento": { "forma": "cartao", "numero_cartao": "4111111111111111" }
}

// resposta 201
{
  "id": 1,
  "status": "ativa",
  "pet": "cao",
  "porte": "medio",
  "plano": "trimestral",
  "valor_por_caixa": "84.90",
  "proxima_entrega": "2026-12-24",
  "entrega_atual": { "status": "Pago" }
}
```

`GET /api/assinaturas/minha` (precisa de login)

```json
// resposta 200 (mesmo formato da resposta acima)
{
  "id": 1,
  "status": "ativa",
  "pet": "cao",
  "porte": "medio",
  "plano": "trimestral",
  "valor_por_caixa": "84.90",
  "proxima_entrega": "2026-12-24",
  "entrega_atual": { "status": "Pago" }
}

// resposta 404 (cliente sem assinatura não cancelada)
{ "detail": "Você não tem uma assinatura" }
```

Erro de assinatura duplicada:

```json
// resposta 409
{ "detail": "Você já tem uma assinatura" }
```

**Regras:**
- Nome obrigatório, e-mail válido, CEP com 8 dígitos (o front manda sem o traço).
- `forma` é `pix` ou `cartao`. Com cartão, `numero_cartao` com 16 dígitos.
- A assinatura nasce `ativa`, e a caixa atual nasce com status `Pago`.
- `proxima_entrega` = hoje + 1 mês.
- Se o cliente já tem uma assinatura não cancelada: `409`.

**Tarefas:**
- [ ] Entidade `Assinatura` no `domain/` com status, plano, pet, porte, próxima entrega e status da caixa atual.
- [ ] Tabela `assinaturas` e migration.
- [ ] Repositório com `salvar` e `buscar_ativa_do_usuario`.
- [ ] Caso de uso `assinar`, que usa o cálculo da HU05 e registra o pagamento pela fachada de `pagamentos` (HU19; enquanto não existir, deixar um ponto para ligar depois).
- [ ] `facade.py` com `eh_membro(usuario_id)`, que o fluxo da loja vai usar.
- [ ] Rotas.
- [ ] Testes: assinatura ok, CEP inválido, cartão inválido, assinatura duplicada.

## Fluxo: Gerenciar a assinatura

Todas as rotas precisam de login e agem sobre a assinatura do usuário logado. Todas devolvem a assinatura atualizada, no mesmo formato do `GET /api/assinaturas/minha`.

### HU07: Pausar e retomar

> Como assinante, quero pausar o Clube por um tempo sem perder minha assinatura.

**Endpoints:** `POST /api/assinaturas/minha/pausar` e `POST /api/assinaturas/minha/retomar`

Nenhum dos dois tem corpo na requisição.

```json
// resposta 200 do pausar
{
  "id": 1,
  "status": "pausada",
  "pet": "cao",
  "porte": "medio",
  "plano": "trimestral",
  "valor_por_caixa": "84.90",
  "proxima_entrega": "2026-12-24",
  "entrega_atual": { "status": "Pago" }
}

// resposta 409 (ex.: pausar uma assinatura já pausada)
{ "detail": "Só é possível pausar uma assinatura ativa" }
```

**Regras:**
- Pausar só se estiver `ativa`. Retomar só se estiver `pausada`. Fora disso: `409`.

**Tarefas:**
- [ ] Métodos `pausar()` e `retomar()` na entidade, que lançam erro de regra quando não pode.
- [ ] Casos de uso e rotas.
- [ ] Testes de cada transição permitida e proibida.

### HU08: Pular a próxima caixa

> Como assinante, quero pular a caixa do próximo mês.

**Endpoint:** `POST /api/assinaturas/minha/pular` (sem corpo na requisição)

```json
// resposta 200 (proxima_entrega era 2026-12-24)
{
  "id": 1,
  "status": "ativa",
  "pet": "cao",
  "porte": "medio",
  "plano": "trimestral",
  "valor_por_caixa": "84.90",
  "proxima_entrega": "2027-01-24",
  "entrega_atual": { "status": "Pago" }
}

// resposta 409
{ "detail": "Só é possível pular a caixa de uma assinatura ativa" }
```

**Regras:**
- Só com a assinatura `ativa`. Senão, `409`.
- `proxima_entrega` avança um mês.

**Tarefas:**
- [ ] Método `pular_caixa()` na entidade.
- [ ] Caso de uso e rota.
- [ ] Testes: pular ativa, pular pausada, pular cancelada.

### HU09: Trocar de plano

> Como assinante, quero trocar de plano sem cancelar a assinatura.

**Endpoint:** `POST /api/assinaturas/minha/trocar-plano`

```json
// requisição
{ "plano": "anual" }

// resposta 200 (cão porte médio: 69,90 + 5,00)
{
  "id": 1,
  "status": "ativa",
  "pet": "cao",
  "porte": "medio",
  "plano": "anual",
  "valor_por_caixa": "74.90",
  "proxima_entrega": "2026-12-24",
  "entrega_atual": { "status": "Pago" }
}

// resposta 409
{ "detail": "A assinatura já está nesse plano" }
```

**Regras:**
- Não pode trocar se estiver `cancelada` (`409`).
- Trocar para o mesmo plano: `409`.
- O novo plano vale a partir da próxima cobrança. `valor_por_caixa` passa a ser o do novo plano.

**Tarefas:**
- [ ] Método `trocar_plano()` na entidade.
- [ ] Caso de uso e rota.
- [ ] Testes.

### HU10: Cancelar

> Como assinante, quero cancelar o Clube.

**Endpoint:** `POST /api/assinaturas/minha/cancelar` (sem corpo na requisição)

```json
// resposta 200 (a caixa já paga continua com o status dela)
{
  "id": 1,
  "status": "cancelada",
  "pet": "cao",
  "porte": "medio",
  "plano": "trimestral",
  "valor_por_caixa": "84.90",
  "proxima_entrega": null,
  "entrega_atual": { "status": "Enviado" }
}

// resposta 409
{ "detail": "A assinatura já está cancelada" }
```

**Regras:**
- `ativa` ou `pausada` → `cancelada`. Cancelar o que já está cancelado: `409`.
- Não tem volta. Para voltar, o cliente assina de novo (HU06).
- A caixa já paga continua sendo entregue (o status da caixa atual não muda).

**Tarefas:**
- [ ] Método `cancelar()` na entidade.
- [ ] Caso de uso e rota.
- [ ] Testes: cancelar ativa, cancelar pausada, cancelar de novo, assinar de novo depois de cancelar.

### HU11: Histórico da assinatura (se der tempo)

> Como assinante, quero ver o histórico do que fiz na assinatura.

**Endpoint:** `GET /api/assinaturas/minha/historico`

```json
// resposta 200
[
  { "acao": "assinou", "data": "2026-11-24T10:30:00" },
  { "acao": "pausou", "data": "2026-11-28T15:02:00" }
]
```

**Tarefas:**
- [ ] Tabela `historico_assinatura` e migration.
- [ ] Gravar um registro em cada caso de uso das HU06 a HU10.
- [ ] Rota e teste.

## Fluxo: Carrinho e pedidos da loja

O carrinho fica no front. A API só recebe os itens na hora de calcular e de fechar o pedido. Assim não precisa de tabela de carrinho.

### HU12: Calcular os totais do carrinho

> Como cliente, quero ver descontos e frete antes de fechar o pedido.

**Endpoint:** `POST /api/carrinho/totais` (login opcional: sem login, o cliente não é membro)

```json
// requisição
{
  "itens": [
    { "produto_id": 1, "quantidade": 1, "frequencia_dias": 30 },
    { "produto_id": 7, "quantidade": 2, "frequencia_dias": null }
  ]
}

// resposta 200
{
  "subtotal": "229.70",
  "desconto_programada": "9.50",
  "desconto_membro": "22.02",
  "frete": "0.00",
  "total": "198.18",
  "membro": true
}
```

**Regras:**
- `frequencia_dias` é `30`, `45`, `60` ou `null` (compra única). Só pode ter frequência se o produto aceita programada; senão, `422`.
- `desconto_programada` = 5% sobre os itens com frequência.
- `desconto_membro` = 10% sobre (`subtotal` − `desconto_programada`). Só para membro.
- Membro é quem tem assinatura com status diferente de `cancelada` (perguntar para a fachada de `assinaturas`).
- `frete` = R$ 14,90. Grátis se for membro **e** o valor com descontos for de pelo menos R$ 150.
- Os preços vêm do banco (fachada do `catalogo`), nunca do front.

**Tarefas:**
- [ ] Função de cálculo no `domain/`, sem banco.
- [ ] Caso de uso que busca os produtos no `catalogo` e o status de membro em `assinaturas`.
- [ ] Rota.
- [ ] Testes: sem desconto, só programada, só membro, os dois juntos, frete grátis no limite de R$ 150.

### HU13: Finalizar pedido da loja

> Como cliente, quero finalizar minha compra.

**Endpoint:** `POST /api/pedidos` (precisa de login)

```json
// requisição
{
  "itens": [
    { "produto_id": 1, "quantidade": 1, "frequencia_dias": 30 },
    { "produto_id": 7, "quantidade": 2, "frequencia_dias": null }
  ],
  "cep": "37500000",
  "forma_pagamento": "pix"
}

// resposta 201
{
  "id": 10,
  "status": "Pago",
  "criado_em": "2026-11-30T14:00:00",
  "itens": [
    { "produto_id": 1, "nome": "Ração Premium Cães Adultos 10kg", "quantidade": 1, "preco_unitario": "189.90", "frequencia_dias": 30 }
  ],
  "subtotal": "229.70",
  "desconto_programada": "9.50",
  "desconto_membro": "22.02",
  "frete": "0.00",
  "total": "198.18"
}
```

**Regras:**
- Lista de itens vazia: `422`.
- CEP com 8 dígitos.
- `forma_pagamento`: `pix`, `cartao` ou `boleto`.
- Totais calculados com a mesma função da HU12.
- O pedido nasce `Pago`.
- Cada item com frequência gera uma compra programada (HU16), com próxima entrega = hoje + frequência.

**Tarefas:**
- [ ] Entidades `Pedido` e `ItemPedido` no `domain/`.
- [ ] Tabelas `pedidos` e `itens_pedido` e migration.
- [ ] Repositório.
- [ ] Caso de uso `finalizar_pedido`: calcula, salva o pedido, cria as compras programadas e registra o pagamento (HU19).
- [ ] Rota.
- [ ] Testes: pedido ok, carrinho vazio, CEP inválido, item programado gera compra programada.

### HU14: Listar meus pedidos

> Como cliente, quero ver meus pedidos e onde cada um está.

**Endpoint:** `GET /api/pedidos` (precisa de login)

Devolve a lista de pedidos do usuário, do mais novo para o mais antigo. Cada item tem o mesmo formato da resposta da HU13. Sem pedidos, devolve `[]`.

```json
// resposta 200
[
  {
    "id": 10,
    "status": "Enviado",
    "criado_em": "2026-11-30T14:00:00",
    "itens": [
      { "produto_id": 1, "nome": "Ração Premium Cães Adultos 10kg", "quantidade": 1, "preco_unitario": "189.90", "frequencia_dias": 30 },
      { "produto_id": 7, "nome": "Petisco Bifinho de Frango", "quantidade": 2, "preco_unitario": "19.90", "frequencia_dias": null }
    ],
    "subtotal": "229.70",
    "desconto_programada": "9.50",
    "desconto_membro": "22.02",
    "frete": "0.00",
    "total": "198.18"
  }
]
```

**Tarefas:**
- [ ] Repositório com `listar_do_usuario`.
- [ ] Rota.
- [ ] Teste: um usuário não vê o pedido do outro.

### HU15: Avançar o status do pedido

> Como operador da demo, quero avançar o status de um pedido para simular a entrega.

**Endpoints:**
- `POST /api/pedidos/{id}/avancar-status` para pedidos da loja.
- `POST /api/assinaturas/minha/avancar-entrega` para a caixa do Clube.

Nenhum dos dois tem corpo na requisição. Cada um devolve o recurso atualizado: o pedido (formato da HU13) ou a assinatura (formato da HU06).

```json
// resposta 200 de POST /api/pedidos/10/avancar-status (estava "Pago")
{
  "id": 10,
  "status": "Separando",
  "criado_em": "2026-11-30T14:00:00",
  "itens": [ ... ],
  "subtotal": "229.70",
  "desconto_programada": "9.50",
  "desconto_membro": "22.02",
  "frete": "0.00",
  "total": "198.18"
}

// resposta 200 de POST /api/assinaturas/minha/avancar-entrega (estava "Pago")
{
  "id": 1,
  "status": "ativa",
  "pet": "cao",
  "porte": "medio",
  "plano": "trimestral",
  "valor_por_caixa": "84.90",
  "proxima_entrega": "2026-12-24",
  "entrega_atual": { "status": "Separando" }
}

// resposta 409
{ "detail": "O pedido já foi entregue" }
```

**Regras:**
- Sequência fixa: `Pago` → `Separando` → `Enviado` → `Entregue`.
- `Entregue` não avança mais: `409`.

**Tarefas:**
- [ ] A sequência de status e a função `proximo_status` no `domain/` de cada módulo (são poucas linhas, pode repetir).
- [ ] Casos de uso e rotas.
- [ ] Testes: cada passo e o `409` no final.

## Fluxo: Compra programada

Fica no módulo `pedidos`. Todas as rotas precisam de login.

### HU16: Listar minhas compras programadas

> Como cliente, quero ver minhas compras programadas e a próxima entrega de cada uma.

**Endpoint:** `GET /api/compras-programadas`

```json
// resposta 200
[
  {
    "id": 3,
    "produto_id": 1,
    "nome_produto": "Ração Premium Cães Adultos 10kg",
    "quantidade": 1,
    "frequencia_dias": 30,
    "status": "ativa",
    "proxima_entrega": "2026-12-30"
  }
]
```

**Regras:**
- Canceladas não aparecem.

**Tarefas:**
- [ ] Entidade `CompraProgramada` no `domain/`.
- [ ] Tabela `compras_programadas` e migration (pode ir junto com a da HU13, combinar com quem pegou).
- [ ] Repositório e rota.
- [ ] Teste: cancelada não aparece.

### HU17: Pausar, retomar, pular e cancelar

> Como cliente, quero controlar minhas compras programadas.

**Endpoints** (todos devolvem a compra programada atualizada):
- `POST /api/compras-programadas/{id}/pausar`
- `POST /api/compras-programadas/{id}/retomar`
- `POST /api/compras-programadas/{id}/pular`
- `POST /api/compras-programadas/{id}/cancelar`

Nenhum tem corpo na requisição.

```json
// resposta 200 do pular (frequência de 30 dias, proxima_entrega era 2026-12-30)
{
  "id": 3,
  "produto_id": 1,
  "nome_produto": "Ração Premium Cães Adultos 10kg",
  "quantidade": 1,
  "frequencia_dias": 30,
  "status": "ativa",
  "proxima_entrega": "2027-01-29"
}

// resposta 409 (ex.: retomar uma compra que não está pausada)
{ "detail": "Só é possível retomar uma compra programada pausada" }

// resposta 404 (não existe ou é de outro usuário)
{ "detail": "Compra programada não encontrada" }
```

**Regras:**
- `ativa` ⇄ `pausada`. `ativa` ou `pausada` → `cancelada`, sem volta. Transição inválida: `409`.
- Pular soma a frequência (30, 45 ou 60 dias) à próxima entrega.
- Compra programada de outro usuário: `404`.

**Tarefas:**
- [ ] Métodos na entidade.
- [ ] Casos de uso e rotas.
- [ ] Testes de cada transição.

### HU18: Trocar a frequência (se der tempo)

> Como cliente, quero mudar de quanto em quanto tempo recebo um item.

**Endpoint:** `POST /api/compras-programadas/{id}/trocar-frequencia`

```json
// requisição
{ "frequencia_dias": 45 }

// resposta 200 (era 30 dias com proxima_entrega 2026-12-30; somou 15)
{
  "id": 3,
  "produto_id": 1,
  "nome_produto": "Ração Premium Cães Adultos 10kg",
  "quantidade": 1,
  "frequencia_dias": 45,
  "status": "ativa",
  "proxima_entrega": "2027-01-14"
}
```

**Regras:**
- Só 30, 45 ou 60 (senão, `422`).
- A próxima entrega muda pela diferença: de 30 para 45 dias, soma 15; de 60 para 30, subtrai 30.

**Tarefas:**
- [ ] Método `trocar_frequencia()` na entidade.
- [ ] Caso de uso e rota.
- [ ] Testes: aumentar, diminuir, frequência inválida.

## Fluxo: Pagamentos

### HU19: Registrar pagamento simulado (se der tempo)

> Como sistema, quero registrar cada cobrança para ter o histórico de pagamentos.

**Sem endpoint público.** Os outros módulos chamam pela fachada.

```python
# pagamentos/facade.py
def registrar_pagamento(usuario_id: int, origem: str, origem_id: int, forma: str, valor: Decimal) -> int: ...
```

**Regras:**
- `origem` é `pedido` ou `assinatura`.
- `forma`: `pix`, `cartao` ou `boleto`.
- O gateway é simulado e sempre aprova.

**Tarefas:**
- [ ] Entidade `Pagamento`, tabela `pagamentos` e migration.
- [ ] Gateway simulado no `adapters/`, atrás de uma interface no `ports.py`.
- [ ] Fachada.
- [ ] Ligar nas HU06 e HU13.
- [ ] Teste do registro.

## Resumo dos endpoints

| Método | Rota | Login | História |
|---|---|---|---|
| POST | `/api/contas` | não | HU01 |
| POST | `/api/contas/login` | não | HU02 |
| GET | `/api/contas/eu` | sim | HU02 |
| GET | `/api/produtos` | não | HU03 |
| GET | `/api/produtos/{id}` | não | HU03 |
| GET | `/api/planos` | não | HU04 |
| POST | `/api/assinaturas/simulacao` | não | HU05 |
| POST | `/api/assinaturas` | sim | HU06 |
| GET | `/api/assinaturas/minha` | sim | HU06 |
| POST | `/api/assinaturas/minha/pausar` | sim | HU07 |
| POST | `/api/assinaturas/minha/retomar` | sim | HU07 |
| POST | `/api/assinaturas/minha/pular` | sim | HU08 |
| POST | `/api/assinaturas/minha/trocar-plano` | sim | HU09 |
| POST | `/api/assinaturas/minha/cancelar` | sim | HU10 |
| GET | `/api/assinaturas/minha/historico` | sim | HU11 |
| POST | `/api/assinaturas/minha/avancar-entrega` | sim | HU15 |
| POST | `/api/carrinho/totais` | opcional | HU12 |
| POST | `/api/pedidos` | sim | HU13 |
| GET | `/api/pedidos` | sim | HU14 |
| POST | `/api/pedidos/{id}/avancar-status` | sim | HU15 |
| GET | `/api/compras-programadas` | sim | HU16 |
| POST | `/api/compras-programadas/{id}/pausar` | sim | HU17 |
| POST | `/api/compras-programadas/{id}/retomar` | sim | HU17 |
| POST | `/api/compras-programadas/{id}/pular` | sim | HU17 |
| POST | `/api/compras-programadas/{id}/cancelar` | sim | HU17 |
| POST | `/api/compras-programadas/{id}/trocar-frequencia` | sim | HU18 |
