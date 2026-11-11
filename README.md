# Assistentes de IA e tempo de implementação em projetos de código aberto: resultados preliminares com dados públicos de um experimento aleatorizado

Projeto Final de **MCEQ 12576 – Métodos de Computação Experimental e Quantitativa** (PUC-Campinas, 2º sem. 2026).
Equipe: Bruno Arias Alves Cruz, Felipe Corso Pretoni, Victor Reis de Palma.

## Pergunta
Em desenvolvedores experientes de código aberto resolvendo *issues* reais de seus próprios repositórios, a permissão de uso de assistentes de IA está associada à redução do tempo de implementação, comparada à proibição do uso?

- H0: µ_IA ≥ µ_semIA  · H1: µ_IA < µ_semIA (unilateral, α = 0,05)
- Plano completo, registrado antes da análise: [`PROTOCOLO.md`](PROTOCOLO.md)

## Origem dos dados
| Item | Valor |
|---|---|
| Estudo | Becker, Rush, Barnes, Rein (2025). *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity*. arXiv:2507.09089 |
| Arquivo | `data_complete.csv` (246 tarefas, 16 desenvolvedores) |
| Fonte | https://github.com/METR/Measuring-Early-2025-AI-on-Exp-OSS-Devs |
| Versão | commit `7ff2d7670235f531dff77eff58355bd77392f396` · SHA-256 do CSV `1493fc46dc37…` |
| Data de acesso | 11/11/2026 |
| Licença | Não declarada no repositório de origem. Por isso **o CSV não é redistribuído aqui**: `baixar_dados.py` o baixa da fonte na versão fixa. |
| Medição | Tempos em minutos registrados pelos próprios desenvolvedores; tarefa sorteada para "IA permitida" ou "IA proibida" (ver artigo original, Seção 2 e Apêndice G). |

## Como reexecutar
```bash
python -m venv .venv && source .venv/bin/activate   # opcional
pip install -r requirements.txt
python baixar_dados.py     # baixa dados/brutos/data_complete.csv e confere o hash
python analise.py          # gera dados/limpos/, resultados/ e figuras/figura1.png
python graficos_apresentacao.py   # (opcional) gráficos do vídeo: figuras/slide_*.png
```
No Google Colab: faça upload dos dois `.py` e do `requirements.txt`, rode `!pip install -r requirements.txt`, depois `!python baixar_dados.py` e `!python analise.py`.

Saída esperada (resumo, em `resultados/resultados.txt`):
- Teste t pareado unilateral (16 desenvolvedores): t(15) = 1,702; p = 0,945 → **não rejeita H0**
- Razão de médias geométricas IA/sem IA = 1,295 (IC 95%: 0,937 a 1,791); d_z = 0,425
- Exploratória E2 reproduz o resultado dos autores: +18,8% (IC 95%: +1,3% a +39,5%)

## Estrutura
```
baixar_dados.py          # download na versão fixa + verificação de hash
analise.py               # dados brutos -> limpos -> descritiva, testes, figura
graficos_apresentacao.py # gráficos usados no vídeo, a partir dos resultados da análise
PROTOCOLO.md             # plano registrado antes da análise
dados/brutos/            # (gerado) CSV original, nunca editado à mão
dados/limpos/            # (gerado) tarefas_limpas.csv, medias_por_desenvolvedor.csv
resultados/              # (gerado) resultados.txt, descritiva.csv
figuras/                 # (gerado) figura1.png e slide_*.png
```

## Decisões de análise (ver protocolo)
- **Desenho em blocos**: cada desenvolvedor recebeu as duas condições (sorteio por tarefa), então o desenvolvedor é o bloco e a análise confirmatória é pareada (Aula 07).
- **Escala log**: tempos são assimétricos à direita; a diferença de médias de log-tempo vira razão de médias geométricas.
- **Teste alternativo pré-definido**: Wilcoxon, caso Shapiro-Wilk rejeitasse a normalidade das diferenças (não rejeitou: p = 0,93).
- **Exclusões**: só tempos ausentes ou ≤ 0 (nenhuma tarefa foi excluída).
- Análises não planejadas estão marcadas como **exploratórias** no código e no artigo.
