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
- grade semanal com prevenção de conflitos;
- tópicos e subtópicos de conteúdo;
- sessões com objetivo, prioridade, duração e conclusão;
- telas Hoje, Semana, Progresso, Avaliações e Metas;
- análise de notas por disciplina;
- metas adaptativas por notas, dificuldade ou pendências;
- tema claro/escuro persistido;
- branch `local-demo` sem Google e sem MongoDB Atlas.

## Rodar em dois minutos

### Demonstração local

Não exige Secrets, Google ou banco externo. Os dados são temporários.

```bash
git clone -b local-demo git@github.com:caldasdv/IhcStreamlitApp.git
cd IhcStreamlitApp
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

- identidade fixa `local-demo-user`;
- `mongomock` em memória;
- um semestre de exemplo com disciplinas, conteúdos, sessões, grade e avaliações;
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
app.py                 entrypoint
app_pages/             páginas do Streamlit
src/ui/                shell, estilos e componentes
src/services/          casos de uso
src/domain/            regras testáveis
src/repositories/      interfaces e MongoDB
src/database/          conexão e índices
tests/                 testes unitários
assets/                identidade visual
```

## Testar

```bash
python -m pytest -q
python -m compileall -q app.py app_pages src tests
python -m pip check
```

Os testes unitários não exigem Google, Secrets ou Atlas.

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

`main` só recebe alterações após revisão e autorização de merge.

## Segurança

O Plano identifica usuários por `identity.provider + identity.subject`, não apenas por e-mail. Leituras e escritas privadas são filtradas pelo usuário autenticado, e credenciais ficam fora do código e do histórico Git.
