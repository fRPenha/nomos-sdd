# Nomos

> **Status:** projeto experimental / MVP

Nomos é uma **camada local-first de especificação, contratos e preparação de tarefas para agentes de implementação**.

Ele foi iniciado como um **fork do [GitHub Spec Kit](https://github.com/github/spec-kit)**, reaproveitando a base de CLI e parte da infraestrutura do projeto original, mas com um objetivo diferente: **transformar ideias e demandas em um pacote claro, verificável e executável por outro agente**, como Codex, Claude Code, Gemini CLI ou equivalente.

## O que é o Nomos

O Nomos não é o agente que implementa.

O Nomos é a ferramenta responsável por:

- entender a demanda dentro do contexto do repositório atual;
- organizar entrevistas e descoberta;
- consolidar especificações funcionais e técnicas;
- registrar regras, restrições, critérios de aceite e decisões;
- estruturar análise de impacto;
- gerar plano e tarefas;
- produzir um pacote final para um agente de implementação.

Em outras palavras, o Nomos fica entre a ideia e a implementação:

```text
Ideia
↓
Nomos
↓
Especificação + Contratos + Regras + Critérios + Plano + Tarefas + Agent Package
↓
Codex / Claude Code / Gemini CLI / outro agente
↓
Implementação
```

## De onde ele deriva

O Nomos nasceu como uma adaptação do GitHub Spec Kit.

O Spec Kit original é orientado a um fluxo de **Spec-Driven Development** focado em gerar especificações, planos e tarefas para implementação dentro do próprio ecossistema do projeto. O Nomos aproveita essa base inicial, mas muda o centro de gravidade do produto:

- o Spec Kit original é mais voltado a **scaffold de fluxo SDD**;
- o Nomos é voltado a **preparação local de contexto, contratos e handoff** para outro agente executar.

## Qual problema o Nomos tenta resolver

Em muitos times, a implementação começa cedo demais e a formalização vem tarde demais.

Isso costuma gerar:

- ambiguidade sobre o que deve ser feito;
- retrabalho por falta de escopo claro;
- impacto inesperado em sistemas legados;
- dificuldade de usar agentes de codificação com segurança;
- documentação desconectada da demanda real.

O Nomos tenta resolver esse problema criando uma etapa intermediária explícita: **antes de implementar, formalize a demanda localmente dentro do repositório**.

## Diferença entre Nomos e o Spec Kit original

O Nomos não deve ser entendido como um simples rebranding.

As diferenças de posicionamento são estas:

| Tema | Spec Kit original | Nomos |
| --- | --- | --- |
| Objetivo principal | Estruturar fluxo SDD | Formalizar demanda e preparar handoff |
| Workspace inicial | `.specify/`, `specs/` e integrações | `.nomos/` dentro do repositório |
| Papel do agente | Pode participar do fluxo completo até implementação | Prepara o pacote para outro agente implementar |
| Fonte da verdade local | Artefatos do fluxo Spec Kit | Artefatos em `.nomos/` |
| Estado atual | Projeto-base consolidado | Camada nova, experimental e incremental |

## Finalidade da pasta `.nomos/`

Na primeira fase, o Nomos trabalha dentro do repositório e grava seus artefatos em `.nomos/`.

Essa pasta é:

- local ao projeto;
- adicionada ao `.gitignore` por padrão;
- a fonte da verdade local da demanda durante o trabalho com o Nomos;
- o ponto de handoff para o agente de implementação.

No futuro, a equipe pode decidir:

- versionar partes de `.nomos/`;
- exportar artefatos oficiais para `specs/`, `docs/` ou outro destino;
- transformar o Nomos em um fluxo formal do time.

## Como o Nomos funciona hoje

O Nomos atual introduz uma camada local de trabalho dentro do repositório:

1. inicializa `.nomos/`;
2. registra conhecimento do projeto em `.nomos/project/`;
3. organiza descoberta em `.nomos/discovery/`;
4. organiza backlog em `.nomos/backlog/`;
5. organiza planejamento em `.nomos/planning/`;
6. cria demandas em `.nomos/demands/<demand-id>/`;
7. produz um `agent-package.md` inicial para consumo por um agente implementador.

Nesta fase, ele continua sendo um **método guiado por agentes**: não executa descoberta automática inteligente, mas já fornece trilho, templates e checkpoints para transformar uma ideia ampla em demandas implementáveis.

## Fluxo recomendado

```text
Ideia ampla
↓
Discovery
↓
Backlog
↓
Planning
↓
Demand
↓
Specification
↓
Agent Package
↓
Implementation
```

## Comandos iniciais

### Inicializar o workspace Nomos

```bash
specify nomos init
```

Cria `.nomos/` no repositório atual, inicializa a estrutura base e adiciona `.nomos/` ao `.gitignore` se a regra ainda não existir.

### Inicializar com perfil explícito

```bash
specify nomos init --profile advpl
```

Usa um perfil inicial para registrar contexto do projeto em `.nomos/project/profile.json`. Nesta fase, o perfil ainda é simples, mas já prepara o terreno para comportamentos mais especializados.

### Inicializar a camada Discovery / Backlog / Planning

```bash
specify nomos planning init
```

Cria os artefatos base em `.nomos/discovery/`, `.nomos/backlog/` e `.nomos/planning/`.

### Verificar o status da camada de planejamento

```bash
specify nomos planning status
```

Mostra quais diretórios e artefatos já existem, quais estão ausentes e qual é o próximo passo sugerido.

### Criar uma nova demanda

```bash
specify nomos demand create minha-demanda
```

Cria uma demanda em:

```text
.nomos/demands/minha-demanda/
```

### Criar uma demanda com título amigável

```bash
specify nomos demand create minha-demanda --title "Título da demanda"
```

Além do identificador técnico da demanda, grava um título legível nos arquivos gerados.

## Como usar o Nomos em outro projeto

O fluxo principal desta fase é:

1. clonar `nomos-sdd` uma vez;
2. instalar a CLI localmente a partir desse checkout;
3. usar `specify nomos ...` em qualquer outro repositório Git.

### Fluxo principal com `uv tool install`

Pré-requisitos:

- `uv` instalado;
- Python 3.11+;
- um checkout local deste repositório.

Do diretório `nomos-sdd`, você pode instalar com o script de conveniência:

```bash
./tools/install-nomos-local.sh
```

No Windows PowerShell:

```powershell
.\tools\install-nomos-local.ps1
```

Se preferir rodar o comando diretamente:

```bash
uv tool install --from /caminho/para/nomos-sdd specify-cli
```

Depois disso, em outro repositório:

```bash
cd ~/Projetos/RCA-Navigator
specify nomos init
specify nomos planning init
specify nomos demand create minha-demanda
```

Se você alterar o código local do Nomos e quiser reinstalar a versão do checkout, rode novamente o mesmo comando. Se precisar forçar reinstalação, passe os argumentos suportados pelo `uv tool install`, por exemplo:

```bash
./tools/install-nomos-local.sh --force
```

### Alternativa com `pipx install -e`

Se você já usa `pipx`, a alternativa local é:

```bash
pipx install -e /caminho/para/nomos-sdd
```

Esse fluxo também expõe `specify` no ambiente do usuário, mas nesta fase ele é apenas a alternativa documentada. O caminho principal recomendado continua sendo `uv tool install --from ...`.

### Fallback com `uv run --project`

Se você não quiser uma instalação persistente, ou estiver depurando o ambiente, use:

```bash
uv run --project /caminho/para/nomos-sdd specify nomos init
uv run --project /caminho/para/nomos-sdd specify nomos demand create minha-demanda
```

Esse fallback funciona sem ativar a `.venv`, mas não é o fluxo principal porque mantém o uso acoplado ao caminho do checkout.

## Estrutura de diretórios criada

Após `specify nomos init`, a estrutura inicial é:

```text
.nomos/
├── project/
│   ├── project.json
│   ├── profile.json
│   ├── glossary.md
│   ├── conventions.md
│   └── architecture-notes.md
├── demands/
├── exports/
├── private/
├── cache/
└── current
```

Após `specify nomos planning init`, o workspace passa a incluir:

```text
.nomos/
├── project/
├── discovery/
│   ├── project-snapshot.md
│   ├── current-architecture.md
│   ├── target-architecture.md
│   ├── risks-and-constraints.md
│   └── open-questions.md
├── backlog/
│   ├── backlog.md
│   ├── demand-map.md
│   ├── dependency-map.md
│   └── readiness-criteria.md
├── planning/
│   ├── product-brief.md
│   ├── roadmap.md
│   ├── next-demand.md
│   └── agent-planning-brief.md
├── demands/
└── current
```

Ao criar uma demanda, o Nomos gera:

```text
.nomos/demands/<demand-id>/
├── demand.json
├── interview.md
├── discovery.md
├── impact-analysis.md
├── functional-spec.md
├── technical-spec.md
├── business-rules.md
├── acceptance-criteria.md
├── constraints.md
├── decisions.md
├── implementation-plan.md
├── tasks.md
├── agent-package.md
├── contracts/
│   └── README.md
└── prompts/
    └── README.md
```

## O que é uma demanda no Nomos

Uma demanda é a unidade local de formalização de trabalho dentro do Nomos.

Ela representa um problema, mudança ou funcionalidade que precisa ser preparada antes da implementação. Uma demanda agrupa:

- contexto de descoberta;
- especificação funcional;
- especificação técnica;
- regras e restrições;
- critérios de aceite;
- plano de implementação;
- tarefas;
- pacote de handoff.

## O que entra em Discovery, Backlog e Planning

Antes de criar uma demanda específica, o Nomos agora separa o raciocínio em três camadas:

- `discovery/`: fotografia do projeto, arquitetura atual, arquitetura desejada, riscos, restrições e perguntas em aberto;
- `backlog/`: mapa de demandas candidatas, dependências, ordem de implementação e critérios de prontidão;
- `planning/`: resumo executivo, roadmap, próxima demanda recomendada e briefing compacto para agentes.

Essa separação reduz a quantidade de tokens que um agente precisa gastar para descobrir o projeto do zero em cada sessão.

## O que é o `agent-package.md`

O `agent-package.md` é o **ponto de entrada do agente de implementação**.

Ele organiza o dossiê local da demanda e orienta qual sequência de arquivos deve ser lida. Em vez de pedir que outro agente tente inferir tudo a partir da conversa, o Nomos explicita:

- qual é a demanda;
- onde estão os artefatos principais;
- quais restrições devem ser respeitadas;
- qual é o escopo esperado;
- o que deve ser produzido.

## Como agentes de implementação devem consumir o pacote

O fluxo esperado é:

1. o desenvolvedor executa o fluxo do Nomos;
2. o Nomos gera ou atualiza a demanda em `.nomos/demands/<demand-id>/`;
3. o agente implementador recebe como ponto de entrada:

```text
.nomos/demands/<demand-id>/agent-package.md
```

4. esse agente lê o `agent-package.md` e, a partir dele, acessa:

- `functional-spec.md`
- `technical-spec.md`
- `impact-analysis.md`
- `business-rules.md`
- `acceptance-criteria.md`
- `constraints.md`
- `implementation-plan.md`
- `tasks.md`
- `contracts/`

Isso vale para Codex, Claude Code, Gemini CLI ou outro agente de codificação que atue sobre o repositório.

## Relação entre `.nomos/` e `specs/`

Nesta fase:

- `.nomos/` é o workspace real do Nomos;
- `specs/` **não** é o destino principal;
- o Nomos ainda não exporta automaticamente artefatos oficiais para `specs/`.

No futuro, `specs/` pode se tornar:

- um destino de exportação oficial;
- uma versão publicável da demanda;
- um espaço de colaboração versionada, se a equipe decidir formalizar isso.

## Versionamento nesta fase

O comportamento padrão atual é:

```gitignore
.nomos/
```

Ou seja:

- `.nomos/` é local por padrão;
- `specify nomos init` adiciona essa regra ao `.gitignore`;
- o conteúdo gerado não depende de versionamento para funcionar;
- futuramente a equipe pode remover ou ajustar essa regra e decidir o que passa a ser versionado.

## Validação local da implementação

Para a entrega atual, a verificação mínima recomendada é:

```bash
python3 -m compileall src/specify_cli/commands/nomos src/specify_cli/_assets.py tests/nomos/test_nomos_cli.py
```

Se o ambiente de desenvolvimento tiver as dependências de teste instaladas, rode também:

```bash
python3 -m pytest tests/nomos/test_nomos_cli.py -v
```

Os testes cobrem o fluxo mínimo de:

- `specify nomos init`
- `specify nomos demand create <demand-id>`

## Compatibilidade com o Spec Kit original

Nesta fase, o Nomos preserva o funcionamento original do fork:

- `specify_cli` não foi renomeado;
- o binário continua sendo `specify`;
- comandos existentes continuam disponíveis;
- o namespace novo é `specify nomos`;
- a infraestrutura herdada do Spec Kit continua intacta.

Isso permite evoluir o Nomos de forma incremental sem quebrar o comportamento já existente.

## Evolução futura

O objetivo de longo prazo é que o Nomos possa evoluir para um CLI próprio, com superfície dedicada, por exemplo:

```bash
nomos init
nomos start
nomos demand create ...
```

Essa evolução ainda não faz parte desta fase. O foco atual é validar o produto e a estrutura conceitual dentro do fork existente.

Importante: `nomos` não deve surgir como alias trivial de `specify_cli:main`, porque `nomos init` e `specify init` têm semânticas diferentes. Quando essa evolução for tratada, ela deve receber um entrypoint dedicado e manter compatibilidade com `specify nomos`.

## Roadmap inicial

O roadmap atual do projeto é:

1. consolidar `.nomos/` como workspace local de demandas;
2. enriquecer a criação de demandas e o `agent-package.md`;
3. introduzir perfis mais úteis, como `advpl`;
4. adicionar capacidades consultivas e análise de impacto;
5. estruturar exportação futura para artefatos oficiais;
6. avaliar a transição para um CLI próprio do Nomos.

## Público-alvo

O Nomos é pensado para:

- desenvolvedores;
- analistas de sistemas;
- arquitetos de software;
- pessoas que trabalham com agentes de codificação;
- equipes que precisam formalizar demandas antes da implementação.

## Instalação e base atual

Enquanto o Nomos continua evoluindo dentro deste fork, a base de CLI ainda é a do projeto original.

Hoje, o ponto de entrada continua sendo:

```bash
specify
```

e os comandos do Nomos entram por:

```bash
specify nomos ...
```

## Aviso importante

O Nomos ainda está em fase inicial.

Mesmo com uma estrutura funcional mínima, ele deve ser tratado como:

- experimental;
- em evolução;
- sujeito a mudanças de ergonomia, nomenclatura e formato dos artefatos.

Se a proposta provar valor em uso real, a próxima etapa natural é consolidar o fluxo consultivo e o handoff para agentes como capacidade central do produto.

## Licença

Este repositório mantém a licença do projeto-base. Consulte [LICENSE](./LICENSE).
