# Protocolo do Projeto Final – MCEQ 12576 (máx. 1 página)

**Registrado em 11/11/2026, antes de qualquer análise dos resultados.** Até esta data só foram conferidos a estrutura do arquivo (colunas, valores ausentes e número de tarefas por desenvolvedor em cada condição), sem comparar tempos entre os grupos.

| Campo | Conteúdo |
|---|---|
| **EQUIPE / MEMBROS** | Bruno Arias Alves Cruz, Felipe Corso Pretoni, Victor Reis de Palma |
| **PROBLEMA (lacuna)** | Assistentes de IA são adotados em larga escala, mas a magnitude do efeito sobre o tempo de desenvolvimento varia com a tarefa, o ambiente e os participantes. Osorio et al. (2025) observaram redução de tempo com Copilot em tarefas acadêmicas curtas; falta evidência sobre tarefas reais em projetos maduros. |
| **PERGUNTA DE PESQUISA** | Em desenvolvedores experientes de código aberto resolvendo *issues* reais de seus próprios repositórios, a permissão de uso de assistentes de IA está associada à redução do tempo de implementação da tarefa, comparada à proibição do uso? |
| **H0** | µ_IA ≥ µ_semIA (o tempo médio, em escala log, com IA permitida não é menor) |
| **H1** (☒ unilateral ☐ bilateral) | µ_IA < µ_semIA (com IA permitida o tempo é menor). Na análise pareada: µ_d < 0, com d = média(log t \| IA) − média(log t \| sem IA) por desenvolvedor. |
| **VI (fator) e níveis** | Uso de IA: *permitido* (ai_treatment = 1) × *proibido* (ai_treatment = 0), sorteado por tarefa. |
| **VD e unidade** | Tempo de implementação inicial (min) até abrir o PR para revisão (`initial_implementation_time`), analisado em escala log (razão de médias geométricas). |
| **CONTROLE / MODERADORA** | Bloco: desenvolvedor (cada um recebeu as duas condições). Controle: todos experientes no próprio repositório. Moderadora da ficha (familiaridade com a ferramenta de IA) **não existe na base** → não testada. |
| **O QUE MUDOU EM RELAÇÃO À FICHA** | (1) Contexto: de "tarefas de complexidade equivalente" para *issues* reais sorteadas; (2) VD: de segundos até passar nos testes para minutos até o PR (variável disponível); (3) desenho: de grupos independentes para blocos por desenvolvedor; (4) moderadora indisponível. Motivo: não há coleta própria (R4); adaptamos à base pública. |
| **BASE ESCOLHIDA** | METR – *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity* (Becker et al., 2025, arXiv:2507.09089). Arquivo `data_complete.csv`, repositório github.com/METR/Measuring-Early-2025-AI-on-Exp-OSS-Devs, commit `7ff2d76`, acesso em 11/11/2026. Licença: **não declarada**; dados publicados pelos autores para replicação → não redistribuímos, só baixamos por script. |
| **JUSTIFICATIVA DA BASE** | Proveniência: artigo + autores + versão fixa (commit). Documentação: dicionário de variáveis no README. Tamanho: 246 tarefas, 16 devs, todos com as duas condições. VD e VI existem diretamente. Medição: tempos registrados pelos próprios desenvolvedores (ver ameaças). |
| **TIPO DE ESTUDO** | ☒ experimento publicado (aleatorizado por tarefa) ☐ observacional |
| **DESENHO** | ☐ 2 grupos indep. ☒ pareado/blocos (bloco = desenvolvedor) ☐ k tratamentos |
| **UNIDADE DE ANÁLISE e n** | Desenvolvedor (n = 16 pares de médias); tarefas: 246 (136 com IA, 110 sem IA). |
| **TESTE PREVISTO, α e estatística** | Teste t pareado unilateral sobre d (diferença de médias de log-tempo por desenvolvedor), α = 0,05. |
| **TESTE ALTERNATIVO** | Se Shapiro-Wilk em d der p < 0,05: Wilcoxon de postos sinalizados unilateral. Definido agora. |
| **TAMANHO DE EFEITO E IC** | d_z = média(d)/dp(d) (d de Cohen pareado); razão de médias geométricas exp(média d) com IC 95% bilateral. |
| **AMEAÇAS À VALIDADE INICIAIS** | Conclusão: n = 16 devs, baixo poder. Interna: tempo autorrelatado; sem cegamento; nº desigual de tarefas por dev. Construção: "tempo até o PR" ≠ produtividade (ignora qualidade). Externa: devs muito experientes, projetos maduros, ferramentas do início de 2025. |

**Análises exploratórias (rótulo obrigatório, não confirmatórias):** (E1) Welch no nível da tarefa, ignorando o bloco, para comparar com o pareado (Aula 07); (E2) tempo total (inicial + pós-revisão) com a imputação dos autores; (E3) tempo previsto × tempo real. Todo teste feito será contado no artigo.
