# Plano de ajustes de UX e IHC

## Objetivo

Melhorar a clareza, acessibilidade e eficiência da interface sem trocar a paleta Sapphire Nightfall Whisper atualmente aplicada.

O foco será reduzir a carga cognitiva, fortalecer a hierarquia visual e tornar os estados do sistema mais compreensíveis.

## Base da análise

- Heurísticas de Nielsen: visibilidade do estado do sistema, consistência, prevenção de erros, reconhecimento em vez de memorização e design minimalista.
- Lei de Hick: reduzir o tempo de decisão diminuindo ações simultâneas.
- Lei de Fitts: manter ações principais grandes, próximas e fáceis de atingir.
- WCAG: revisar contraste, foco visível, uso de cor e feedback acessível.
- Princípios de hierarquia tipográfica, alinhamento, proximidade e consistência visual.

## Prioridade 1 — Acessibilidade visual

### Ajustes

- Trocar o outline de foco claro por `#0474C4` ou `#06457F`.
- Revisar textos secundários em `#5379AE` sobre fundos claros.
- Confirmar contraste dos estados de hover, foco, erro e desabilitado.
- Garantir que estados não dependam somente da cor.
- Manter texto e ícones da barra lateral em branco sobre o fundo azul escuro.

### Critérios de conclusão

- Todos os elementos interativos possuem foco visível.
- O foco permanece legível em fundo claro e escuro.
- Status de sessão continuam identificáveis por texto e símbolo, além da cor.

## Prioridade 2 — Hierarquia e navegação

### Ajustes

- Reduzir os botões de navegação contextual exibidos simultaneamente.
- Manter uma ação primária clara por tela.
- Mover ações secundárias para uma área menos dominante quando necessário.
- Trocar rótulos em caixa alta por sentence case.
- Revisar o uso dos `eyebrows` para que indiquem contexto real, e não apenas decoração.

### Critérios de conclusão

- Cada tela possui uma ação principal facilmente identificável.
- A navegação não compete visualmente com o conteúdo principal.
- Os títulos podem ser escaneados rapidamente por usuários novos.

## Prioridade 3 — Formulários e prevenção de erros

### Ajustes

- Agrupar campos relacionados por proximidade.
- Usar exemplos nos placeholders somente quando ajudarem a preencher o campo.
- Mostrar mensagens de erro próximas do campo ou ação que falhou.
- Diferenciar visualmente salvar, cancelar e excluir.
- Exigir confirmação clara para ações destrutivas.

### Critérios de conclusão

- O usuário entende o que precisa preencher sem depender de conhecimento técnico.
- Erros indicam o problema e a próxima ação possível.
- Ações destrutivas não podem ser acionadas por engano.

## Prioridade 4 — Feedback e estados do sistema

### Ajustes

- Substituir exceções técnicas por mensagens orientativas na interface.
- Manter traceback e detalhes de infraestrutura apenas nos logs.
- Padronizar estados de carregamento, sucesso, alerta, erro e vazio.
- Garantir que todo estado vazio ofereça uma próxima ação.
- Usar “Tentar novamente” quando a falha for temporária, como indisponibilidade do banco.

### Critérios de conclusão

- O usuário sabe o que aconteceu.
- O usuário sabe se precisa esperar, corrigir um campo ou tentar novamente.
- Estados vazios não parecem telas quebradas.

## Prioridade 5 — Tabelas, gráficos e dados

### Ajustes

- Melhorar leitura dos cabeçalhos das tabelas.
- Garantir comportamento compreensível em telas menores.
- Reduzir repetição entre gráficos e tabelas.
- Destacar apenas os dados relevantes para a decisão atual.
- Preservar filtros e seleções com indicação visual clara.

### Critérios de conclusão

- Tabelas podem ser lidas sem depender da cor.
- Gráficos possuem títulos e legendas compreensíveis.
- A relação entre filtro, gráfico e tabela fica evidente.

## Prioridade 6 — Composição visual

### Ajustes

- Reduzir a quantidade de cards, bordas e sombras.
- Reservar `#0474C4` para ações, seleção e destaque.
- Usar `#A8C4EC` principalmente em superfícies, preenchimentos e estados suaves.
- Usar `#06457F` para estrutura, menu e títulos de maior importância.
- Manter o fundo e os blocos de conteúdo visualmente leves.
- Remover elementos decorativos que não expliquem uma relação ou ação.

### Critérios de conclusão

- O olhar identifica primeiro o objetivo e a ação principal da tela.
- Elementos decorativos não competem com dados ou formulários.
- A interface mantém personalidade sem parecer carregada.

## Ordem de execução sugerida

1. Corrigir foco, contraste e estados interativos.
2. Ajustar a barra lateral e a hierarquia de navegação.
3. Simplificar cabeçalhos e ações contextuais.
4. Revisar formulários, confirmações e mensagens de erro.
5. Revisar tabelas, gráficos e responsividade.
6. Fazer uma última limpeza de cards, bordas, sombras e decoração.

## Validação final

- Testar navegação somente pelo teclado.
- Conferir foco em modo claro e escuro.
- Testar telas vazias, erros de banco e formulários inválidos.
- Conferir visual em desktop e viewport estreito.
- Validar que ações principais continuam evidentes.
- Executar testes automatizados após cada etapa relevante.
