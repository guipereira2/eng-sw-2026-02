# Ciclo Box

E-commerce, desenvolvido na disciplina de Engenharia de Software.

## Como rodar

Pré-requisitos: [uv](https://docs.astral.sh/uv/) e Docker.

```bash
docker compose up -d db
cd backend
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn ciclobox.main:app --reload
```

- Aplicação: http://localhost:8000
- Documentação da API: http://localhost:8000/api/docs
- Saúde da API e do banco: http://localhost:8000/api/health

Se a porta 5432 estiver ocupada, use `POSTGRES_PORT=5433 docker compose up -d db` e ajuste a porta no `backend/.env`.

## Checagens

Dentro de `backend/`, rode o mesmo que o CI:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run lint-imports
uv run pytest                     # precisa do Postgres
uv run pytest -m "not integration" # só testes sem I/O
```

## Estrutura

```text
frontend/             Interface
backend/src/ciclobox/
  assinaturas/        Clube, planos e ciclo da assinatura
  pagamentos/         Cobranças e gateway simulado
  catalogo/           Produtos
  contas/             Usuários e autenticação
  shared/             Configuração, banco e saúde da aplicação
backend/migrations/   Migrations do Alembic
```

Cada módulo tem a mesma organização:

- `domain/`: regras puras, sem framework nem banco.
- `application/`: casos de uso que coordenam o domínio e os efeitos.
- `adapters/`: rotas HTTP, banco e integrações.
- `ports.py`: interfaces de que o módulo precisa.
- `facade.py`: única entrada permitida para outros módulos.
