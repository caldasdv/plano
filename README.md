<div align="center">

<img src="assets/plan-wordmark.svg" alt="Plano — Seu espaço de estudos" width="420" />

# Plano

### Um espaço calmo para planejar, estudar e perceber o progresso.

Organize o semestre, transforme conteúdos em próximos passos e ajuste seu ritmo com base no que está acontecendo.

[Abrir aplicação publicada](https://planejadordeestudos.streamlit.app/)

</div>

## O produto

O Plano é um planejador acadêmico para estudantes:

```text
PLANEJAR → AGENDAR → ESTUDAR → REGISTRAR → ANALISAR → REPLANEJAR
```

O fluxo cobre períodos, disciplinas, grade de aulas, conteúdos, sessões, avaliações e progresso. As metas adaptativas sugerem como distribuir o tempo usando notas, dificuldade e pendências, com regras explicáveis.

## Recursos

- Google OIDC e isolamento por identidade do provedor;
- períodos acadêmicos e disciplinas do período atual;
- grade semanal de aulas com prevenção de conflitos;
- conteúdos (tópicos e subtópicos) por disciplina;
- sessões com objetivo, prioridade, duração, conclusão e opção de desfazer;
- análise de notas por disciplina;
- metas adaptativas por notas, dificuldade ou pendências;
- boas-vindas, assistente "Montar meu plano" e Ajuda para quem está começando;
- tema claro/escuro persistido na conta;
- acessibilidade WCAG 2.1 AA conferida com axe-core nos dois temas;
- branch `local-demo` sem Google e sem MongoDB Atlas.

## Como o app é organizado

A barra lateral tem quatro lugares fixos, na ordem do ciclo de estudo:

| Lugar | Para que serve |
|---|---|
| **Hoje** | o que fazer agora: "Nova sessão", meta da semana, sessões do dia e "Primeiros passos" para quem está começando |
| **Semana** | agenda com sessões e aulas lado a lado; editar ou excluir uma sessão |
| **Progresso** | meta semanal, carga por disciplina e notas |
| **Disciplinas** | período atual e um cartão por disciplina com Conteúdos, Horários, Planejar sessão e Editar |

Abaixo do cartão da conta ficam Ajuda, modo claro/escuro e Sair, no mesmo estilo da navegação.

Cadastrar e editar acontece sempre em pop-up, e só um fica aberto por vez. No primeiro acesso, as boas-vindas oferecem três caminhos:

- **Montar meu plano agora**: assistente em pop-up com período, disciplina, horário de aula, conteúdo e primeira sessão. Horário e conteúdo podem ser pulados, e o assistente retoma de onde parou.
- **Mostrar onde fica cada coisa**: balões que apontam para os itens reais da tela.
- **Agora não**: fecha e registra na conta que as boas-vindas já foram vistas.

A Ajuda reúne perguntas frequentes e mostra os balões de novo.

## Rodar em dois minutos

### Demonstração local

Não exige Secrets, Google ou banco externo. Os dados são temporários.

```bash
git clone -b local-demo git@github.com:caldasdv/plano.git
cd plano
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
PLANO_LOCAL_MODE=true python -m streamlit run app.py
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
$env:PLANO_LOCAL_MODE="true"
python -m streamlit run app.py
```

O `mise` é opcional: `PLANO_LOCAL_MODE=true mise exec -- python -m streamlit run app.py`.

### Ambiente real

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Configure `.streamlit/secrets.toml` a partir de [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example), com MongoDB Atlas e Google OIDC. Nunca versione Secrets ou `.env`.

Para ver dados numa conta vazia, entre no app uma vez com o Google e carregue um semestre de exemplo a partir da raiz do repositório. Sem `--apply` o script só simula, e `--remove --apply` apaga o que ele criou.

```bash
python scripts/seed_sample_account.py --email voce@exemplo.com --apply
```

## Modo local

Ative somente com `PLANO_LOCAL_MODE=true`:

- entrada pela demonstração (`local-demo-user`, com dados prontos) ou por "Começar com plano vazio" (`local-empty-user`, ideal para ver as boas-vindas e o assistente);
- `mongomock` em memória;
- um mês de aulas, sessões e avaliações em seis disciplinas;
- dados descartados ao encerrar o processo;
- mesmos services e repositories do ambiente real.

## Arquitetura

```text
Streamlit UI / Pages → Application Services → Domain + Repository contracts → MongoDB repositories → Atlas ou mongomock local
```

O projeto é um monólito modular. As páginas não acessam o banco diretamente; regras ficam fora do Streamlit e podem ser testadas sem iniciar a aplicação.

| Camada | Responsabilidade |
|---|---|
| `app_pages/` e `src/ui/` | telas, navegação, componentes e feedback |
| `src/services/` | casos de uso e coordenação |
| `src/domain/` | validações, estados e regras puras |
| `src/repositories/` | contratos e adapters de persistência |
| `src/database/` | conexão, índices e modo local |

## Estrutura

```text
app.py                     entrypoint
app_pages/                 as quatro telas: overview (Hoje), weekly, progress, subjects
src/ui/                    shell, navegação, barra lateral, estilos e feedback
src/ui/components/         componentes visuais (agenda, balões, diálogo de sessão, gráficos)
src/ui/sections/           blocos de tela (períodos, cartões de disciplina, metas, notas)
src/ui/forms.py            formulários compartilhados entre pop-ups e assistente
src/ui/onboarding.py       boas-vindas, balões, Ajuda e "Primeiros passos"
src/ui/setup_wizard.py     assistente "Montar meu plano"
src/ui/dialog_state.py     garante um pop-up aberto por vez
src/services/              casos de uso
src/domain/                regras testáveis
src/repositories/          interfaces e MongoDB
src/database/              conexão, índices e dados de exemplo
scripts/                   seed de conta de exemplo
tests/                     testes unitários e de interface (AppTest)
assets/                    identidade visual
```

## Testar

```bash
python -m pytest -q
python -m compileall -q app.py app_pages src tests
python -m pip check
```

Os testes não exigem Google, Secrets ou Atlas. Os testes de interface usam `streamlit.testing.v1.AppTest` no modo local e cobrem a navegação, os pop-ups, o assistente e as boas-vindas.

## Branches

```text
main                  produção
dev                   integração de desenvolvimento
feature/*             funcionalidades em revisão
local-demo            clone executável sem infraestrutura externa
```

Fluxo recomendado:

```bash
git switch dev
git pull --ff-only origin dev
git switch -c feature/nome-da-mudanca
# implementar e testar
git push -u origin feature/nome-da-mudanca
```

`main` só recebe alterações após revisão e autorização de merge. Depois de cada merge na `main`, a `local-demo` é atualizada por um PR `main → local-demo`.

## Segurança

O Plano identifica usuários por `identity.provider + identity.subject`, não apenas por e-mail. Leituras e escritas privadas são filtradas pelo usuário autenticado, e credenciais ficam fora do código e do histórico Git.
