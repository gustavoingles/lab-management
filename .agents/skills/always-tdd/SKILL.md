# Always TDD

## Objetivo

Garantir que o desenvolvimento neste repositório siga Test-Driven Development (TDD): escrever testes antes do código de produção, progredir pelo ciclo Red → Green → Refactor, e manter cobertura de testes adequada.

## Quando aplicar

- Em todas as novas funcionalidades e correções de bugs.
- Em refatorações que alterem comportamento observável.

## Regras e práticas

- Ciclo TDD: 1) Escrever um teste que falha (Red). 2) Implementar o mínimo para fazê-lo passar (Green). 3) Refatorar mantendo testes passando (Refactor).
- Priorizar testes unitários; adicionar testes de integração para fluxos críticos (autenticação, movimentações, ordens de serviço).
- Usar os frameworks de teste do projeto (Django TestCase / pytest conforme configurado).
- Testes devem ser executáveis localmente com: `uv run python manage.py test`.

## Enforcements recomendados

- Pipeline CI: falhar o build quando testes falharem ou quando cobertura estiver abaixo do limiar definido.
- Hooks pré-commit: executar uma suíte de testes rápida (linters + testes unitários rápidos) antes de commits/PRs.

## Dicas práticas

- Comece por escrever testes para as regras de negócio (services, modelos) antes de endpoints/serializers.
- Mantenha testes pequenos, determinísticos e independentes.
- Use fixtures e factories para criar dados de teste reutilizáveis.

## Comandos úteis

- Rodar todos os testes: `uv run python manage.py test`
- Rodar testes em um app: `uv run python manage.py test <app_label>`

## Metadados

- skill: always-tdd
- author: GitHub Copilot (assistente)
