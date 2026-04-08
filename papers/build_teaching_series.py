from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from textwrap import dedent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PAPERS_ROOT = PROJECT_ROOT / "papers"
SBC_TEMPLATE = PAPERS_ROOT / "sbc-template.sty"
SBC_BST = PAPERS_ROOT / "sbc.bst"


ARTICLE_DIRS = {
    "01": PAPERS_ROOT / "01_motivacao_e_negocio",
    "02": PAPERS_ROOT / "02_fundamentos_de_rc",
    "03": PAPERS_ROOT / "03_primeiro_modelo_previsao",
    "04": PAPERS_ROOT / "04_memoria_nao_linearidade",
    "05": PAPERS_ROOT / "05_avaliacao_e_boas_praticas",
    "06": PAPERS_ROOT / "06_rc_fisico_e_ponte_para_qrc",
    "07": PAPERS_ROOT / "07_qrc_para_previsao_de_demanda",
}


def latest_prefixed_dir(parent: Path, prefix: str) -> Path:
    candidates = sorted(path for path in parent.glob(f"{prefix}*") if path.is_dir())
    if not candidates:
        raise FileNotFoundError(f"no directory with prefix {prefix!r} under {parent}")
    return candidates[-1]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: float, digits: int = 3) -> str:
    return f"{float(value):.{digits}f}"


def pct(value: float, digits: int = 2) -> str:
    return f"{100.0 * float(value):.{digits}f}%"


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def figure_block(results_dir_name: str, filename: str, caption: str) -> str:
    return f"![{caption}]({results_dir_name}/{filename})"


WORD_REPLACEMENTS = [
    ("nao", "não"),
    ("tambem", "também"),
    ("ate", "até"),
    ("alem", "além"),
    ("ja", "já"),
    ("ha", "há"),
    ("sera", "será"),
    ("serao", "serão"),
    ("so", "só"),
    ("voce", "você"),
    ("voces", "vocês"),
    ("tres", "três"),
    ("serie", "série"),
    ("series", "séries"),
    ("didatico", "didático"),
    ("didaticos", "didáticos"),
    ("didatica", "didática"),
    ("didaticas", "didáticas"),
    ("memoria", "memória"),
    ("memorias", "memórias"),
    ("reservatorio", "reservatório"),
    ("reservatorios", "reservatórios"),
    ("sequencia", "sequência"),
    ("sequencias", "sequências"),
    ("negocio", "negócio"),
    ("negocios", "negócios"),
    ("otimizacao", "otimização"),
    ("pedagogica", "pedagógica"),
    ("pedagogicas", "pedagógicas"),
    ("pedagogico", "pedagógico"),
    ("pedagogicos", "pedagógicos"),
    ("reposicao", "reposição"),
    ("previsao", "previsão"),
    ("previsoes", "previsões"),
    ("comparacao", "comparação"),
    ("comparacoes", "comparações"),
    ("configuracao", "configuração"),
    ("configuracoes", "configurações"),
    ("organizacao", "organização"),
    ("contribuicao", "contribuição"),
    ("introducao", "introdução"),
    ("conclusao", "conclusão"),
    ("implementacao", "implementação"),
    ("implementacoes", "implementações"),
    ("formulacao", "formulação"),
    ("avaliacao", "avaliação"),
    ("avaliacoes", "avaliações"),
    ("validacao", "validação"),
    ("regularizacao", "regularização"),
    ("simulacao", "simulação"),
    ("representacao", "representação"),
    ("representacoes", "representações"),
    ("interacao", "interação"),
    ("relacao", "relação"),
    ("relacoes", "relações"),
    ("funcao", "função"),
    ("funcoes", "funções"),
    ("equacao", "equação"),
    ("equacoes", "equações"),
    ("dimensao", "dimensão"),
    ("dimensoes", "dimensões"),
    ("regressao", "regressão"),
    ("intuicao", "intuição"),
    ("competicao", "competição"),
    ("abstracoes", "abstrações"),
    ("discussao", "discussão"),
    ("discussoes", "discussões"),
    ("extensao", "extensão"),
    ("operacao", "operação"),
    ("operacoes", "operações"),
    ("reproducao", "reprodução"),
    ("reproducoes", "reproduções"),
    ("reproduzivel", "reproduzível"),
    ("reproduziveis", "reproduzíveis"),
    ("comeca", "começa"),
    ("comecam", "começam"),
    ("comecamos", "começamos"),
    ("comecar", "começar"),
    ("informacao", "informação"),
    ("informacoes", "informações"),
    ("distincao", "distinção"),
    ("proximo", "próximo"),
    ("proximos", "próximos"),
    ("proxima", "próxima"),
    ("proximas", "próximas"),
    ("criterio", "critério"),
    ("criterios", "critérios"),
    ("metodo", "método"),
    ("metodos", "métodos"),
    ("capitulo", "capítulo"),
    ("capitulos", "capítulos"),
    ("metrica", "métrica"),
    ("metricas", "métricas"),
    ("media", "média"),
    ("medias", "médias"),
    ("medio", "médio"),
    ("medios", "médios"),
    ("mediana", "mediana"),
    ("familia", "família"),
    ("familias", "famílias"),
    ("variavel", "variável"),
    ("variaveis", "variáveis"),
    ("periodo", "período"),
    ("periodos", "períodos"),
    ("frequencia", "frequência"),
    ("minimo", "mínimo"),
    ("minimos", "mínimos"),
    ("minima", "mínima"),
    ("minimas", "mínimas"),
    ("maximo", "máximo"),
    ("maximos", "máximos"),
    ("maxima", "máxima"),
    ("maximas", "máximas"),
    ("basico", "básico"),
    ("basicos", "básicos"),
    ("basica", "básica"),
    ("basicas", "básicas"),
    ("classico", "clássico"),
    ("classicos", "clássicos"),
    ("classica", "clássica"),
    ("classicas", "clássicas"),
    ("quantico", "quântico"),
    ("quanticos", "quânticos"),
    ("quantica", "quântica"),
    ("quanticas", "quânticas"),
    ("estatistico", "estatístico"),
    ("estatisticos", "estatísticos"),
    ("estatistica", "estatística"),
    ("estatisticas", "estatísticas"),
    ("teorico", "teórico"),
    ("teoricos", "teóricos"),
    ("teorica", "teórica"),
    ("teoricas", "teóricas"),
    ("tecnica", "técnica"),
    ("tecnicas", "técnicas"),
    ("tecnico", "técnico"),
    ("tecnicos", "técnicos"),
    ("academico", "acadêmico"),
    ("academicos", "acadêmicos"),
    ("academica", "acadêmica"),
    ("academicas", "acadêmicas"),
    ("cientifica", "científica"),
    ("cientificas", "científicas"),
    ("cientifico", "científico"),
    ("cientificos", "científicos"),
    ("fisico", "físico"),
    ("fisicos", "físicos"),
    ("fisica", "física"),
    ("fisicas", "físicas"),
    ("dinamica", "dinâmica"),
    ("dinamicas", "dinâmicas"),
    ("logica", "lógica"),
    ("logistico", "logístico"),
    ("logistica", "logística"),
    ("matematica", "matemática"),
    ("matematicas", "matemáticas"),
    ("matematico", "matemático"),
    ("matematicos", "matemáticos"),
    ("metodologico", "metodológico"),
    ("metodologicos", "metodológicos"),
    ("metodologica", "metodológica"),
    ("metodologicas", "metodológicas"),
    ("exogeno", "exógeno"),
    ("exogenos", "exógenos"),
    ("exogena", "exógena"),
    ("exogenas", "exógenas"),
    ("calendario", "calendário"),
    ("quadratico", "quadrático"),
    ("explicito", "explícito"),
    ("explicitos", "explícitos"),
    ("explicita", "explícita"),
    ("explicitas", "explícitas"),
    ("possivel", "possível"),
    ("possiveis", "possíveis"),
    ("dificil", "difícil"),
    ("dificeis", "difíceis"),
    ("util", "útil"),
    ("uteis", "úteis"),
    ("facil", "fácil"),
    ("faceis", "fáceis"),
    ("historico", "histórico"),
    ("historicos", "históricos"),
    ("decisao", "decisão"),
    ("decisoes", "decisões"),
    ("visao", "visão"),
    ("padrao", "padrão"),
    ("padroes", "padrões"),
    ("promocao", "promoção"),
    ("promocoes", "promoções"),
    ("diaria", "diária"),
    ("diarias", "diárias"),
    ("diario", "diário"),
    ("diarios", "diários"),
    ("codigo", "código"),
    ("codigos", "códigos"),
    ("nucleo", "núcleo"),
    ("seguranca", "segurança"),
    ("politica", "política"),
    ("politicas", "políticas"),
    ("inventario", "inventário"),
    ("desperdicio", "desperdício"),
    ("divisao", "divisão"),
    ("supervisao", "supervisão"),
    ("aleatorio", "aleatório"),
    ("aleatorios", "aleatórios"),
    ("aleatoria", "aleatória"),
    ("aleatorias", "aleatórias"),
    ("treinavel", "treinável"),
    ("treinaveis", "treináveis"),
    ("previa", "prévia"),
    ("previas", "prévias"),
    ("notacao", "notação"),
    ("inicializacao", "inicialização"),
    ("identico", "idêntico"),
    ("identicos", "idênticos"),
    ("identica", "idêntica"),
    ("identicas", "idênticas"),
    ("variacao", "variação"),
    ("questao", "questão"),
    ("questoes", "questões"),
    ("ultimo", "último"),
    ("ultimos", "últimos"),
    ("ultima", "última"),
    ("ultimas", "últimas"),
    ("vao", "vão"),
    ("observavel", "observável"),
    ("observaveis", "observáveis"),
    ("observacao", "observação"),
    ("observacoes", "observações"),
    ("intermediario", "intermediário"),
    ("intermediarios", "intermediários"),
    ("intermediaria", "intermediária"),
    ("intermediarias", "intermediárias"),
    ("estavel", "estável"),
    ("estaveis", "estáveis"),
    ("instavel", "instável"),
    ("instaveis", "instáveis"),
    ("rotacoes", "rotações"),
    ("construido", "construído"),
    ("construidos", "construídos"),
    ("construida", "construída"),
    ("construidas", "construídas"),
    ("distribuido", "distribuído"),
    ("distribuidos", "distribuídos"),
    ("distribuida", "distribuída"),
    ("distribuidas", "distribuídas"),
    ("versao", "versão"),
    ("versoes", "versões"),
    ("nivel", "nível"),
    ("niveis", "níveis"),
    ("unico", "único"),
    ("unicos", "únicos"),
    ("unica", "única"),
    ("unicas", "únicas"),
    ("atras", "atrás"),
    ("rapido", "rápido"),
    ("rapidos", "rápidos"),
    ("rapida", "rápida"),
    ("rapidas", "rápidas"),
    ("hiperparametro", "hiperparâmetro"),
    ("hiperparametros", "hiperparâmetros"),
    ("cosmetico", "cosmético"),
    ("cosmeticos", "cosméticos"),
    ("moveis", "móveis"),
    ("vizinhanca", "vizinhança"),
    ("multiplas", "múltiplas"),
    ("mediocre", "medíocre"),
    ("expressao", "expressão"),
    ("expressoes", "expressões"),
    ("reprodutivel", "reprodutível"),
    ("reprodutiveis", "reprodutíveis"),
]


PHRASE_REPLACEMENTS = [
    ("O objetivo e ", "O objetivo é "),
    ("Isso e ", "Isso é "),
    ("Essa forma e ", "Essa forma é "),
    ("Esse e ", "Esse é "),
    ("Esse erro e ", "Esse erro é "),
    ("Esse vetor e ", "Esse vetor é "),
    ("Este benchmark so e ", "Este benchmark só é "),
    ("Este artigo organiza o benchmark central da serie.", "Este artigo organiza o benchmark central da série."),
    ("Este artigo fecha a serie", "Este artigo fecha a série"),
    ("Este artigo abre a serie", "Este artigo abre a série"),
    ("O foco nao e ", "O foco não é "),
    ("Previsão de demanda e importante", "Previsão de demanda é importante"),
    ("Previsao de demanda e importante", "Previsão de demanda é importante"),
    ("previsão de demanda e um problema central", "previsão de demanda é um problema central"),
    ("esse problema e valioso", "esse problema é valioso"),
    ("ele e dificil", "ele é difícil"),
    ("ele e util", "ele é útil"),
    ("esse problema e uma boa rota", "esse problema é uma boa rota"),
    ("efeito e escrever", "efeito é escrever"),
    ("A previsao e feita por ", "A previsão é feita por "),
    ("A implementacao e curta", "A implementação é curta"),
    ("A dinamica do reservatorio e", "A dinâmica do reservatório é"),
    ("A comparacao direta", "A comparação direta"),
    ("A visao geral", "A visão geral"),
    ("A leitura dos dois pontos e clara", "A leitura dos dois pontos é clara"),
    ("O experimento e didaticamente valioso", "O experimento é didaticamente valioso"),
    ("O ponto metodologico aqui e", "O ponto metodológico aqui é"),
    ("O resultado final e instrutivo", "O resultado final é instrutivo"),
    ("um estudo completo e didático", "um estudo completo e didático"),
    ("em todos os qubits e um anel", "em todos os qubits e um anel"),
    ("O QRC funciona", "O QRC funciona"),
    ("O RC funciona", "O RC funciona"),
    ("RC e atraente", "RC é atraente"),
    ("RC e mais rico", "RC é mais rico"),
    ("QRC-Lab: An Educational Toolbox for Quantum Reservoir Computing", "QRC-Lab: An Educational Toolbox for Quantum Reservoir Computing"),
    ("Em RC, a ideia e diferente.", "Em RC, a ideia é diferente."),
    ("A melhor imagem mental para um iniciante e esta:", "A melhor imagem mental para um iniciante é esta:"),
    ("Essa divisao e importante", "Essa divisão é importante"),
    ("Essa expressao pode ser lida em voz alta assim:", "Essa expressão pode ser lida em voz alta assim:"),
    ("Essa e a parte que transforma o reservatorio", "Essa é a parte que transforma o reservatório"),
    ("Essa leitura e mais importante", "Essa leitura é mais importante"),
    ("Esse ponto e central", "Esse ponto é central"),
    ("Esse ponto didatico aqui e decisivo", "Esse ponto didático aqui é decisivo"),
    ("baseline serio", "baseline sério"),
    ("baselines serios", "baselines sérios"),
    ("comparacao seria", "comparação séria"),
]


def _preserve_case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def accentize_portuguese(text: str) -> str:
    parts = text.split("```")
    for idx in range(0, len(parts), 2):
        segment = parts[idx]
        for source, target in PHRASE_REPLACEMENTS:
            segment = segment.replace(source, target)
        for source, target in WORD_REPLACEMENTS:
            pattern = rf"\b{re.escape(source)}\b"
            segment = re.sub(
                pattern,
                lambda match, repl=target: _preserve_case(match.group(0), repl),
                segment,
                flags=re.IGNORECASE,
            )
        segment = re.sub(r"(\$[^$]+\$) e (?=(a|o|um|uma)\b)", r"\1 é ", segment)
        segment = re.sub(
            r"\bo que e\b",
            lambda match: _preserve_case(match.group(0), "o que é"),
            segment,
            flags=re.IGNORECASE,
        )
        segment = re.sub(
            r"\bnao e\b",
            lambda match: _preserve_case(match.group(0), "não é"),
            segment,
            flags=re.IGNORECASE,
        )
        segment = re.sub(
            r"\bnão e\b",
            lambda match: _preserve_case(match.group(0), "não é"),
            segment,
            flags=re.IGNORECASE,
        )
        parts[idx] = segment
    return "```".join(parts)


def normalize_markdown(text: str) -> str:
    lines = text.splitlines()
    cleaned = [line[8:] if line.startswith("        ") else line for line in lines]
    normalized = "\n".join(cleaned).strip() + "\n"
    return accentize_portuguese(normalized)


def load_context() -> dict[str, dict]:
    context: dict[str, dict] = {}
    for key, article_dir in ARTICLE_DIRS.items():
        results_dir = latest_prefixed_dir(article_dir, "computational_results_")
        context[key] = {"article_dir": article_dir, "results_dir": results_dir}

    context["01"]["summary"] = {
        row["metric"]: row["value"]
        for row in read_csv_rows(context["01"]["results_dir"] / "recorte_summary.csv")
    }
    context["01"]["weekly_profile"] = read_csv_rows(
        context["01"]["results_dir"] / "weekly_profile.csv"
    )

    context["02"]["quality_preview"] = read_csv_rows(
        context["02"]["results_dir"] / "rc_quality_preview.csv"
    )
    context["02"]["seed_stability_summary"] = read_csv_rows(
        context["02"]["results_dir"] / "rc_seed_stability_summary.csv"
    )
    context["02"]["seed_stability_runs"] = read_csv_rows(
        context["02"]["results_dir"] / "rc_seed_stability_runs.csv"
    )
    context["02"]["washout_sweep"] = read_csv_rows(
        context["02"]["results_dir"] / "rc_washout_sweep.csv"
    )

    context["03"]["baseline_vs_rc"] = read_csv_rows(
        context["03"]["results_dir"] / "baseline_vs_rc_metrics.csv"
    )

    context["04"]["sweep_n_reservoir"] = read_csv_rows(
        context["04"]["results_dir"] / "rc_sweep_n_reservoir.csv"
    )
    context["04"]["sweep_spectral_radius"] = read_csv_rows(
        context["04"]["results_dir"] / "rc_sweep_spectral_radius.csv"
    )
    context["04"]["sweep_leak_rate"] = read_csv_rows(
        context["04"]["results_dir"] / "rc_sweep_leak_rate.csv"
    )

    context["05"]["benchmark_metrics"] = read_csv_rows(
        context["05"]["results_dir"] / "benchmark_metrics.csv"
    )
    context["05"]["benchmark_ranked"] = read_csv_rows(
        context["05"]["results_dir"] / "benchmark_ranked.csv"
    )

    context["06"]["qrc_focus_summary"] = read_csv_rows(
        context["06"]["results_dir"] / "qrc_focus_summary.csv"
    )
    context["06"]["qrc_best_objective"] = read_json(
        context["06"]["results_dir"] / "qrc_best_objective.json"
    )
    context["06"]["qrc_best_extended"] = read_json(
        context["06"]["results_dir"] / "qrc_best_qubits_window_extended.json"
    )

    context["07"]["qrc_focus_comparison"] = read_csv_rows(
        context["07"]["results_dir"] / "qrc_focus_comparison.csv"
    )
    context["07"]["qrc_best_objective"] = read_json(
        context["07"]["results_dir"] / "qrc_best_objective.json"
    )
    context["07"]["qrc_best_extended"] = read_json(
        context["07"]["results_dir"] / "qrc_best_qubits_window_extended.json"
    )
    return context


def build_article_01(context: dict[str, dict]) -> str:
    ctx = context["01"]
    results_name = ctx["results_dir"].name
    summary = ctx["summary"]
    weekly = ctx["weekly_profile"]

    summary_table = markdown_table(
        ["Metrica", "Valor"],
        [
            ["Dias totais no recorte", summary["n_total_days"]],
            ["Dias de treino", summary["train_days"]],
            ["Dias de teste", summary["test_days"]],
            ["Media diaria de vendas", fmt(summary["mean_sales"], 2)],
            ["Desvio padrao das vendas", fmt(summary["std_sales"], 2)],
            ["Taxa media de promocao", pct(summary["promotion_rate"])],
            ["Taxa de dias com venda zero", pct(summary["zero_sales_rate"])],
            ["Inicio do treino", summary["train_start"]],
            ["Inicio do teste", summary["test_start"]],
            ["Fim do teste", summary["test_end"]],
        ],
    )

    weekly_table = markdown_table(
        ["Dia da semana", "Media com promocao", "Media sem promocao"],
        [
            [
                row["dow"],
                fmt(row["com promocao"], 2),
                fmt(row["sem promocao"], 2),
            ]
            for row in weekly
        ],
    )

    return dedent(
        rf"""
        # Previsao de demanda e otimizacao de estoque: por que este problema importa

        ## Resumo

        Este primeiro artigo abre a serie com o problema de negocio que vai sustentar todos os experimentos seguintes: previsao de demanda para reposicao de estoque. O objetivo e mostrar por que esse problema e valioso, por que ele e dificil e por que ele cria um caminho didatico natural ate Reservoir Computing (RC) e Quantum Reservoir Computing (QRC). Em vez de comecar pela teoria do reservatorio, comecamos pelo custo do erro no varejo, formalizamos a tarefa de previsao, fixamos o recorte experimental no dataset Favorita e mostramos as primeiras estatisticas reais da serie `store_nbr = 1` e `family = BEVERAGES`. Ao final, o leitor sabe como carregar o recorte, entende as metricas que vao guiar a serie, enxerga o impacto de promocao e calendario e tem um mapa completo dos sete artigos.

        ## 1. O que o leitor vai aprender

        Ao final deste artigo, voce sera capaz de:

        1. explicar por que previsao de demanda e um problema central de negocio;
        2. formular matematicamente a tarefa de previsao da serie;
        3. reproduzir o recorte adotado no Favorita em toda a obra;
        4. interpretar os primeiros artefatos computacionais antes de treinar qualquer modelo;
        5. entender por que esse problema e uma boa rota pedagogica ate QRC.

        ## 2. O problema de negocio antes do modelo

        Previsao de demanda e importante porque o erro entra diretamente na decisao de estoque. Se a empresa compra menos do que deveria, perde venda. Se compra mais, imobiliza capital e aumenta o risco de desperdicio. Em um ambiente de varejo alimentar, isso acontece em escala diaria, com milhares de decisoes pequenas produzindo efeitos acumulados grandes.

        Um modo simples de formalizar esse efeito e escrever o erro de previsao como

        $$
        e_{{t+h}} = y_{{t+h}} - \hat{{y}}_{{t+h}},
        $$

        em que $y_{{t+h}}$ e a demanda observada e $\hat{{y}}_{{t+h}}$ e a previsao produzida no tempo $t$ para o horizonte $h$.

        Esse erro alimenta uma politica operacional minima de reposicao:

        $$
        R_t = \hat{{y}}_{{t+1}} + SS_t,
        $$

        em que $R_t$ e a quantidade planejada para reposicao e $SS_t$ e um estoque de seguranca. Mesmo sem modelar toda a politica de inventario, a equacao deixa claro o ponto principal: melhorar $\hat{{y}}_{{t+1}}$ melhora a qualidade da decisao.

        ## 3. Da pergunta de negocio para a tarefa de previsao

        Ao longo da serie, vamos modelar a tarefa como

        $$
        \hat{{y}}_{{t+h}} = f(y_{{1:t}}, x_{{1:t+h}}),
        $$

        em que:

        - $y_{{1:t}}$ representa o historico de vendas observado ate o tempo $t$;
        - $x_{{1:t+h}}$ representa sinais exogenos, como promocao e calendario;
        - $f(\cdot)$ sera implementada por modelos estatisticos, de IA classica, RC e QRC.

        Essa forma e importante pedagogicamente porque nos permite manter o mesmo problema enquanto trocamos a familia de modelo. O que muda do artigo 1 ao 7 nao e a pergunta. O que muda e a maneira de construir a representacao temporal.

        ## 4. O dataset Favorita e o recorte didatico da serie

        O projeto usa o dataset da competicao *Corporacion Favorita Grocery Sales Forecasting* como fio condutor. Para manter o ensino progressivo e reproduzivel, toda a serie comeca no mesmo recorte:

        - loja: `store_nbr = 1`
        - familia: `BEVERAGES`
        - frequencia: diaria
        - teste: ultimos `90` dias

        A tabela abaixo resume o recorte real usado nas implementacoes.

        {summary_table}

        O carregamento desse recorte e implementado em `code/common/favorita.py`. O nucleo da reproducao e o seguinte:

        ```python
        from common.favorita import (
            FavoritaSeriesConfig,
            load_store_family_series,
            temporal_train_test_split,
        )

        config = FavoritaSeriesConfig(store_nbr=1, family="BEVERAGES", test_days=90)
        frame = load_store_family_series(store_nbr=config.store_nbr, family=config.family)
        train, test = temporal_train_test_split(frame, test_days=config.test_days)
        ```

        Esse codigo faz tres coisas que sao centrais para toda a serie:

        1. fixa um recorte comum para todos os modelos;
        2. densifica o calendario diario, preenchendo dias faltantes com zero;
        3. garante um split temporal identico para comparacoes posteriores.

        ## 5. O que os dados ja ensinam antes de qualquer modelo

        Antes de falar de RC ou QRC, vale observar o comportamento bruto da serie.

        {figure_block(results_name, "series_overview.png", "Visao geral da serie de demanda usada ao longo da serie de artigos.")}

        A visao geral mostra que o problema nao e trivial por pelo menos tres motivos:

        - ha variacao forte ao longo do tempo;
        - a serie responde a padroes semanais;
        - promocao altera o patamar das vendas.

        O perfil semanal medio confirma esse ultimo ponto.

        {weekly_table}

        {figure_block(results_name, "weekly_profile.png", "Perfil semanal medio com e sem promocao no recorte adotado.")}

        Duas leituras didaticas aparecem imediatamente:

        1. a serie tem sazonalidade semanal clara, o que justifica baselines como `Seasonal Naive` e `ETS`;
        2. promocao desloca a media de vendas em todos os dias da semana, o que torna natural incluir variaveis exogenas.

        Esse e o primeiro motivo para escolher esse problema como rota ate QRC: mesmo o recorte inicial ja exige memoria temporal e sensibilidade a contexto.

        ## 6. Passo-a-passo para reproduzir o recorte

        O leitor pode reproduzir o ponto de partida da obra em quatro passos.

        ### 6.1 Passo 1: localizar os dados

        Os arquivos brutos foram organizados em `dataset/raw/`, com `train.csv`, `transactions.csv`, `stores.csv`, `holidays_events.csv`, `oil.csv` e `test.csv`.

        ### 6.2 Passo 2: carregar uma unica serie

        A funcao `load_store_family_series()` filtra por loja e familia, ordena por data e produz um `DataFrame` com as colunas:

        - `ds`: data
        - `y`: demanda diaria
        - `onpromotion`: sinal exogeno basico usado nos modelos

        ### 6.3 Passo 3: fixar o split temporal

        A funcao `temporal_train_test_split()` implementa a regra que vamos herdar em toda a serie:

        - o passado vai para treino;
        - os ultimos `90` dias vao para teste;
        - nenhuma observacao do futuro entra no treino.

        ### 6.4 Passo 4: inspecionar o recorte

        Os artefatos computacionais deste artigo ja mostram o minimo necessario para nao modelar no escuro:

        - `series_overview.png`
        - `weekly_profile.png`
        - `recorte_summary.csv`

        Em um projeto real, essa etapa nao e opcional. Ela evita treinar modelos sofisticados sobre uma serie mal definida.

        ## 7. Como vamos medir desempenho

        Toda a obra usa as mesmas quatro metricas, implementadas em `code/common/metrics.py`.

        O erro absoluto medio e dado por

        $$
        \mathrm{{MAE}} = \frac{{1}}{{n}} \sum_{{t=1}}^n |y_t - \hat{{y}}_t|.
        $$

        O erro quadratico medio com raiz e dado por

        $$
        \mathrm{{RMSE}} = \sqrt{{\frac{{1}}{{n}} \sum_{{t=1}}^n (y_t - \hat{{y}}_t)^2}}.
        $$

        O erro absoluto ponderado pelo volume da serie e dado por

        $$
        \mathrm{{WAPE}} = \frac{{\sum_{{t=1}}^n |y_t - \hat{{y}}_t|}}{{\sum_{{t=1}}^n |y_t|}}.
        $$

        E o erro percentual absoluto medio simetrico e dado por

        $$
        \mathrm{{sMAPE}} = \frac{{1}}{{n}} \sum_{{t=1}}^n
        \frac{{2 |y_t - \hat{{y}}_t|}}{{|y_t| + |\hat{{y}}_t|}}.
        $$

        Essas metricas vao aparecer repetidamente porque cada uma responde a uma pergunta diferente:

        - `MAE`: erro medio em unidades de venda;
        - `RMSE`: sensibilidade a erros grandes;
        - `WAPE`: erro relativo ao volume total;
        - `sMAPE`: comparacao percentual mais estavel em series com escalas diferentes.

        ## 8. Por que esse problema conduz naturalmente ate RC e QRC

        Ha pelo menos quatro motivos.

        1. A serie depende do passado, entao memoria importa.
        2. O efeito de promocao e calendario nao e constante, entao nao linearidade importa.
        3. O protocolo de negocio e simples de explicar, entao o leitor nao se perde no dominio.
        4. O mesmo recorte pode ser usado para modelos estatisticos, IA classica, RC e QRC.

        Em outras palavras, o problema e suficientemente real para ser relevante e suficientemente controlado para ser didatico.

        ## 9. Roadmap dos sete artigos

        O percurso da serie sera o seguinte:

        1. artigo 1: problema de negocio, recorte e metricas;
        2. artigo 2: fundamentos de Reservoir Computing;
        3. artigo 3: primeiro pipeline reproduzivel com baseline e RC;
        4. artigo 4: memoria, nao linearidade e tuning do RC;
        5. artigo 5: benchmark justo entre todas as implementacoes;
        6. artigo 6: ponte de RC classico para QRC;
        7. artigo 7: estudo final de QRC no Favorita.

        Essa organizacao evita um erro comum em textos de QRC: apresentar o formalismo quantico antes de o leitor entender a tarefa, o protocolo experimental e a logica do reservatorio.

        ## 10. Conclusao

        O ponto de partida da serie esta estabelecido. Temos um problema de negocio real, um recorte experimental fixo, um pipeline minimo de carregamento de dados e um conjunto de metricas que permitira comparacoes honestas. Esse chao comum e o que torna possivel ensinar RC e QRC sem perder o leitor em abstracoes.

        O proximo artigo parte daqui para responder a pergunta central que o leitor provavelmente ja esta fazendo: afinal, o que e um reservatorio e por que ele pode ser util para uma serie temporal como essa?

        ## Entregaveis associados no repositorio

        - dados brutos: `dataset/raw/`
        - carga do recorte: `code/common/favorita.py`
        - metricas: `code/common/metrics.py`
        - artefatos deste artigo: `{results_name}/`
        - figuras principais: `series_overview.png` e `weekly_profile.png`

        ## Referencias

        - Corporacion Favorita Grocery Sales Forecasting. Kaggle.
        - Hyndman, R. J.; Athanasopoulos, G. Forecasting: Principles and Practice.
        - Jaeger, H. The "echo state" approach to analysing and training recurrent neural networks.
        - Lukosevicius, M.; Jaeger, H. Reservoir computing approaches to recurrent neural network training.
        """
    ).strip() + "\n"


def build_article_02(context: dict[str, dict]) -> str:
    ctx = context["02"]
    results_name = ctx["results_dir"].name
    preview = {row["model"]: row for row in ctx["quality_preview"]}
    seed_summary = {row["config"]: row for row in ctx["seed_stability_summary"]}
    radius_rows = context["04"]["sweep_spectral_radius"]
    leak_rows = context["04"]["sweep_leak_rate"]
    reservoir_rows = context["04"]["sweep_n_reservoir"]
    washout_rows = sorted(ctx["washout_sweep"], key=lambda row: int(row["washout"]))

    default_label = "RC default (sr=0.60, leak=0.15)"
    contained_label = "RC mais contido (sr=0.20, leak=0.15)"
    contained_fast_label = "RC mais contido e mais rapido (sr=0.20, leak=0.30)"

    default_summary = seed_summary[default_label]
    contained_summary = seed_summary[contained_label]
    contained_fast_summary = seed_summary[contained_fast_label]

    def row_by_value(rows: list[dict[str, str]], value: float) -> dict[str, str]:
        return next(row for row in rows if abs(float(row["value"]) - value) < 1e-12)

    best_washout = min(washout_rows, key=lambda row: float(row["mae"]))
    radius_02 = row_by_value(radius_rows, 0.2)
    radius_06 = row_by_value(radius_rows, 0.6)
    radius_08 = row_by_value(radius_rows, 0.8)
    leak_015 = row_by_value(leak_rows, 0.15)
    leak_03 = row_by_value(leak_rows, 0.3)
    leak_05 = row_by_value(leak_rows, 0.5)
    reservoir_40 = row_by_value(reservoir_rows, 40.0)
    reservoir_80 = row_by_value(reservoir_rows, 80.0)
    reservoir_160 = row_by_value(reservoir_rows, 160.0)

    rc_mae = float(preview["RC"]["mae"])
    seasonal_mae = float(preview["Seasonal Naive"]["mae"])
    ets_mae = float(preview["ETS"]["mae"])
    rc_gap_vs_seasonal = (rc_mae / seasonal_mae - 1.0) * 100.0
    rc_gap_vs_ets = (rc_mae / ets_mae - 1.0) * 100.0
    seed_mae_gain = (1.0 - float(contained_fast_summary["mae_mean"]) / float(default_summary["mae_mean"])) * 100.0
    seed_std_gain = (1.0 - float(contained_fast_summary["mae_std"]) / float(default_summary["mae_std"])) * 100.0

    dimensions_table = markdown_table(
        ["Objeto", "Dimensao no projeto", "Origem"],
        [
            ["Vetor de entrada $u_t$", "7", "`scaled_input_vector()`"],
            ["Estado do reservatorio $x_t$", "80", "`RCConfig.n_reservoir`"],
            ["Vetor de features $[1; u_t; x_t]$", "88", "`_feature_vector()`"],
            ["Readout", "1 saida", "Ridge linear sobre as features"],
        ],
    )

    evaluation_axes_table = markdown_table(
        ["Eixo de avaliacao", "Pergunta correta", "Evidencia usada neste artigo"],
        [
            [
                "Representacao interna",
                "Os estados reagem de forma heterogenea, nao linear e com memoria distribuida?",
                "`sequential_inputs_example.png` e `rc_state_heatmap.png`",
            ],
            [
                "Previsao final",
                "O readout produz erro baixo no mesmo split e contra baselines honestos?",
                "`rc_quality_preview.csv`",
            ],
            [
                "Estabilidade experimental",
                "O resultado se sustenta quando seed e hiperparametros mudam?",
                "`rc_seed_stability_summary.csv` e `rc_washout_sweep.csv`",
            ],
        ],
    )

    quality_preview_table = markdown_table(
        ["Modelo", "Janela", "MAE", "RMSE", "WAPE", "sMAPE"],
        [
            [
                "ETS",
                "teste (90 dias)",
                fmt(preview["ETS"]["mae"]),
                fmt(preview["ETS"]["rmse"]),
                fmt(preview["ETS"]["wape"], 4),
                fmt(preview["ETS"]["smape"], 4),
            ],
            [
                "Seasonal Naive",
                "teste (90 dias)",
                fmt(preview["Seasonal Naive"]["mae"]),
                fmt(preview["Seasonal Naive"]["rmse"]),
                fmt(preview["Seasonal Naive"]["wape"], 4),
                fmt(preview["Seasonal Naive"]["smape"], 4),
            ],
            [
                "RC default",
                "teste (90 dias)",
                fmt(preview["RC"]["mae"]),
                fmt(preview["RC"]["rmse"]),
                fmt(preview["RC"]["wape"], 4),
                fmt(preview["RC"]["smape"], 4),
            ],
        ],
    )

    stability_table = markdown_table(
        ["Configuracao", "Seeds", "MAE", "RMSE", "WAPE", "sMAPE"],
        [
            [
                "default",
                default_summary["n_seeds"],
                f"{fmt(default_summary['mae_mean'])} +/- {fmt(default_summary['mae_std'])}",
                f"{fmt(default_summary['rmse_mean'])} +/- {fmt(default_summary['rmse_std'])}",
                f"{fmt(default_summary['wape_mean'], 4)} +/- {fmt(default_summary['wape_std'], 4)}",
                f"{fmt(default_summary['smape_mean'], 4)} +/- {fmt(default_summary['smape_std'], 4)}",
            ],
            [
                "sr = 0.20",
                contained_summary["n_seeds"],
                f"{fmt(contained_summary['mae_mean'])} +/- {fmt(contained_summary['mae_std'])}",
                f"{fmt(contained_summary['rmse_mean'])} +/- {fmt(contained_summary['rmse_std'])}",
                f"{fmt(contained_summary['wape_mean'], 4)} +/- {fmt(contained_summary['wape_std'], 4)}",
                f"{fmt(contained_summary['smape_mean'], 4)} +/- {fmt(contained_summary['smape_std'], 4)}",
            ],
            [
                "sr = 0.20, leak = 0.30",
                contained_fast_summary["n_seeds"],
                f"{fmt(contained_fast_summary['mae_mean'])} +/- {fmt(contained_fast_summary['mae_std'])}",
                f"{fmt(contained_fast_summary['rmse_mean'])} +/- {fmt(contained_fast_summary['rmse_std'])}",
                f"{fmt(contained_fast_summary['wape_mean'], 4)} +/- {fmt(contained_fast_summary['wape_std'], 4)}",
                f"{fmt(contained_fast_summary['smape_mean'], 4)} +/- {fmt(contained_fast_summary['smape_std'], 4)}",
            ],
        ],
    )

    washout_table = markdown_table(
        ["Washout", "MAE", "RMSE", "WAPE", "sMAPE"],
        [
            [
                row["washout"],
                fmt(row["mae"]),
                fmt(row["rmse"]),
                fmt(row["wape"], 4),
                fmt(row["smape"], 4),
            ]
            for row in washout_rows
        ],
    )

    hyperparameter_table = markdown_table(
        ["Hiperparametro", "Papel", "Faixa inicial pratica", "Evidencia no recorte"],
        [
            [
                "`spectral_radius`",
                "controla persistencia e regime dinamico do reservatorio",
                "`0.20` a `0.60`",
                f"`0.20` gerou MAE {fmt(radius_02['mae'])}; `0.80` degradou para {fmt(radius_08['mae'])}. O default `0.60` ficou em {fmt(radius_06['mae'])}.",
            ],
            [
                "`leak_rate`",
                "controla a velocidade de atualizacao do estado",
                "`0.10` a `0.30`",
                f"`0.30` foi melhor que o default `0.15` ({fmt(leak_03['mae'])} vs. {fmt(leak_015['mae'])}); `0.50` colapsou para {fmt(leak_05['mae'])}.",
            ],
            [
                "`washout`",
                "remove o transiente de inicializacao antes do treino do readout",
                "`7` a `21`",
                f"Nesta serie, o melhor valor testado foi `{best_washout['washout']}` com MAE {fmt(best_washout['mae'])}; acima de `28` o erro voltou a subir.",
            ],
            [
                "`n_reservoir`",
                "define a capacidade representacional do estado interno",
                "`80` como ponto de partida, com vizinhanca `40` a `120`",
                f"`80` foi o melhor ponto entre os testados ({fmt(reservoir_80['mae'])}); `40` subiu para {fmt(reservoir_40['mae'])} e `160` para {fmt(reservoir_160['mae'])}.",
            ],
        ],
    )

    return dedent(
        rf"""
        # Fundamentos de Reservoir Computing: da intuicao ao modelo minimo

        ## Resumo

        Este artigo apresenta Reservoir Computing (RC) como o primeiro grande degrau teorico da serie. O foco nao e apenas definir o termo, mas mostrar como um reservatorio transforma uma sequencia em uma representacao dinamica heterogenea, nao linear e com memoria distribuida. Alem da intuicao e das equacoes, o texto introduz uma camada que faltava na versao anterior: como avaliar o que o RC realmente entrega em tres niveis diferentes: qualidade da representacao interna, qualidade da previsao final e qualidade da estabilidade experimental. No recorte Favorita, o RC classico funciona, produz estados coerentes e previsoes reprodutiveis, mas a configuracao default ainda fica atras de `Seasonal Naive` e `ETS`. Tambem mostramos que seed, `spectral_radius`, `leak_rate`, `washout` e `n_reservoir` mudam materialmente o erro, o que transforma esses hiperparametros em decisoes de projeto, e nao em detalhes cosmeticos.

        ## 1. O que o leitor vai aprender

        Ao final deste artigo, voce sera capaz de:

        1. definir um reservatorio classico de forma matematica;
        2. distinguir estado interno, vetor de entrada e readout;
        3. explicar o papel de `spectral_radius`, `leak_rate` e `washout`;
        4. mapear as equacoes de RC para a implementacao em `code/rc/model.py`;
        5. separar qualidade da representacao interna, qualidade da previsao final e qualidade da estabilidade experimental.

        ## 2. A intuicao: o que um reservatorio faz, antes da equacao

        Em um modelo tabular tradicional, as features costumam ser calculadas explicitamente: lags, medias moveis, indicadores de calendario e assim por diante. Em RC, a ideia e diferente. Em vez de escrever manualmente toda a representacao temporal, injetamos a sequencia em um sistema dinamico recorrente e usamos seus estados internos como uma base de representacao.

        A melhor imagem mental para um iniciante e esta:

        - a entrada $u_t$ entra no sistema no instante atual;
        - o sistema ainda guarda parte do que aconteceu antes;
        - essa mistura entre presente e passado gera um novo estado interno;
        - a previsao final e feita a partir desse estado.

        Em outras palavras, o reservatorio nao tenta prever diretamente. Primeiro ele **transforma a sequencia em estados internos**. So depois o readout aprende a ler esses estados.

        Se quisermos resumir RC em uma frase curta, ela seria:

        > o reservatorio e um mecanismo fixo que converte sequencias em representacoes dinamicas; o readout e a parte treinada que converte essas representacoes em previsao.

        Essa divisao e importante porque reduz a carga conceitual:

        1. primeiro entendemos como o estado interno evolui;
        2. depois entendemos como a previsao sai desse estado.

        ## 3. Construindo o modelo minimo de RC

        Em muitos textos de RC, a equacao do reservatorio aparece pronta, em uma unica linha. Para quem esta vendo o tema pela primeira vez, isso costuma ser brusco demais. Aqui vamos fazer o caminho inverso: comecamos com a pergunta intuitiva, descemos ate um unico passo de atualizacao, olhamos um exemplo de uma unica unidade e so entao escrevemos a equacao completa.

        ### 3.1 A pergunta central em um unico passo

        Em cada instante $t$, o reservatorio recebe uma entrada $u_t$ e mantem internamente um estado $x_{{t-1}}$ vindo do passo anterior. O problema do passo atual pode ser formulado assim:

        > dado o que entrou agora e dado o que o sistema ainda guarda do passado, como produzir o novo estado $x_t$?

        Essa pergunta ja organiza quase todo o raciocinio. O novo estado precisa depender de duas coisas:

        - da entrada atual;
        - da memoria que o proprio sistema traz do passo anterior.

        ### 3.2 Os ingredientes da atualizacao

        Para responder a essa pergunta, o modelo usa:

        - $u_t \in \mathbb{{R}}^d$, o vetor de entrada no tempo $t$;
        - $x_{{t-1}} \in \mathbb{{R}}^N$, o estado interno do passo anterior;
        - $W_{{in}}$, a matriz que projeta a entrada para o espaco do reservatorio;
        - $W_{{res}}$, a matriz recorrente interna, que mistura os componentes do proprio estado;
        - $b$, um vetor de bias;
        - $\alpha \in (0,1]$, o `leak_rate`, que controlara quanto do estado novo realmente entra.

        O ponto principal aqui nao e decorar a notacao. O ponto principal e perceber o papel de cada termo:

        - $W_{{in}} u_t$ traz o **efeito da entrada atual**;
        - $W_{{res}} x_{{t-1}}$ traz o **efeito do passado interno**;
        - $b$ apenas desloca essa resposta;
        - $\alpha$ vai decidir quanto do estado novo substitui o antigo.

        ### 3.3 Primeiro passo: montar a resposta bruta do sistema

        Antes de falar em "estado candidato", vale pensar no que acontece imediatamente quando somamos os efeitos do presente e do passado. Chamaremos essa soma de pre-ativacao:

        $$
        z_t = W_{{res}} x_{{t-1}} + W_{{in}} u_t + b.
        $$

        Essa expressao pode ser lida em voz alta assim:

        > resposta bruta no tempo $t$ = efeito da memoria anterior + efeito da entrada atual + bias.

        O vetor $z_t$ ainda nao e o novo estado final. Ele e apenas a combinacao linear inicial das influencias que atuam sobre o reservatorio naquele instante.

        ### 3.4 Segundo passo: aplicar a nao linearidade

        Se usassemos diretamente $z_t$ como novo estado, o modelo seria linear demais e perderia boa parte da riqueza que queremos em um reservatorio. Por isso, aplicamos uma nao linearidade componente a componente:

        $$
        \widetilde{{x}}_t = \tanh(z_t).
        $$

        Substituindo $z_t$, obtemos:

        $$
        \widetilde{{x}}_t = \tanh(W_{{res}} x_{{t-1}} + W_{{in}} u_t + b).
        $$

        O vetor $\widetilde{{x}}_t$ recebe o nome de **estado candidato**. Ele representa a resposta que o reservatorio produziria se reagisse imediatamente ao passo atual.

        A funcao $\tanh(\cdot)$ tem tres papeis didaticamente importantes:

        - introduz nao linearidade;
        - comprime os valores no intervalo $(-1,1)$;
        - ajuda a manter a dinamica interna em uma faixa controlada.

        Uma maneira simples de sentir isso e olhar alguns valores:

        - se $z = 0.2$, entao $\tanh(0.2) \approx 0.197$;
        - se $z = 3$, entao $\tanh(3) \approx 0.995$;
        - se $z = -4$, entao $\tanh(-4) \approx -0.999$.

        Isso mostra que a nao linearidade nao apenas "entorta" a resposta: ela tambem evita que os valores crescam sem limite.

        ### 3.5 Um exemplo com uma unica unidade

        Para tornar a ideia menos abstrata, imagine por um momento um reservatorio com apenas uma unidade. Nesse caso, todos os vetores e matrizes viram escalares:

        $$
        z_t = w_{{res}} x_{{t-1}} + w_{{in}} u_t + b.
        $$

        Suponha:

        - $x_{{t-1}} = 0.40$;
        - $u_t = 0.70$;
        - $w_{{res}} = 0.50$;
        - $w_{{in}} = 1.20$;
        - $b = -0.10$.

        Entao:

        $$
        z_t = 0.50 \cdot 0.40 + 1.20 \cdot 0.70 - 0.10 = 0.94.
        $$

        Aplicando a nao linearidade:

        $$
        \widetilde{{x}}_t = \tanh(0.94) \approx 0.735.
        $$

        Essa conta simples ajuda a visualizar o processo:

        1. o passado contribui com uma parte;
        2. a entrada atual contribui com outra parte;
        3. tudo isso passa pela `tanh`;
        4. o resultado se torna o estado candidato.

        ### 3.6 Terceiro passo: misturar memoria e atualizacao nova

        O reservatorio ainda nao adota $\widetilde{{x}}_t$ como estado final. Em vez disso, ele mistura parte da memoria anterior com parte do estado candidato:

        $$
        x_t = (1 - \alpha) x_{{t-1}} + \alpha \widetilde{{x}}_t.
        $$

        Essa e a parte que transforma o reservatorio em um sistema com memoria controlada. O parametro $\alpha$ regula a velocidade da atualizacao:

        - se $\alpha$ e pequeno, o sistema preserva mais memoria e muda devagar;
        - se $\alpha$ e grande, o sistema reage mais ao presente e muda mais rapido.

        Voltando ao exemplo anterior, se $x_{{t-1}} = 0.40$, $\widetilde{{x}}_t \approx 0.735$ e $\alpha = 0.20$, entao:

        $$
        x_t = 0.80 \cdot 0.40 + 0.20 \cdot 0.735 \approx 0.467.
        $$

        O leitor deve notar o seguinte: o estado final $x_t$ ainda carrega parte do passado. Ele nao salta diretamente para o estado candidato.

        ### 3.7 A equacao completa do reservatorio

        Agora sim podemos juntar os passos anteriores. Substituindo o estado candidato na equacao de mistura, chegamos a dinamica completa:

        $$
        x_t = (1 - \alpha) x_{{t-1}} + \alpha \tanh(W_{{res}} x_{{t-1}} + W_{{in}} u_t + b).
        $$

        A leitura guiada dessa expressao e:

        - olhe para o passado: $x_{{t-1}}$;
        - combine esse passado com a entrada atual: $W_{{res}} x_{{t-1}} + W_{{in}} u_t + b$;
        - aplique a nao linearidade: $\tanh(\cdot)$;
        - misture o resultado com a memoria anterior usando $\alpha$.

        Essa leitura e mais importante do que decorar a formula.

        ### 3.8 Como isso aparece no codigo

        No codigo, essa construcao aparece de forma quase literal em `EchoStateReservoir.step()`:

        ```python
        pre_activation = (
            self.recurrent_weights @ self.state
            + self.input_weights @ input_vector
            + self.bias
        )
        new_state = np.tanh(pre_activation)
        self.state = (1.0 - self.config.leak_rate) * self.state + self.config.leak_rate * new_state
        ```

        A correspondencia entre teoria e implementacao fica mais facil de ler quando usamos os mesmos tres passos:

        1. `pre_activation` corresponde a $z_t$;
        2. `new_state` corresponde a $\widetilde{{x}}_t$;
        3. `self.state = ...` corresponde a atualizacao final de $x_t$.

        ### 3.9 Como a previsao sai do estado interno

        A dinamica do reservatorio produz uma representacao temporal, mas ainda nao produz a previsao final. Para isso, usamos um readout linear:

        $$
        \hat{{y}}_t = W_{{out}} \phi_t,
        \qquad
        \phi_t = [1; u_t; x_t].
        $$

        O vetor $\phi_t$ concatena tres elementos:

        - um termo constante, representado por `1`;
        - a entrada atual $u_t$;
        - o estado interno $x_t$.

        Em linguagem simples, isso quer dizer: depois que o reservatorio transforma a sequencia em um estado interno, o readout aprende uma combinacao linear dessas informacoes para produzir a previsao.

        No projeto, `\phi_t` e construida por `_feature_vector()` e `W_out` e ajustado via regressao Ridge.

        ## 4. O que e treinado e o que nao e treinado

        Um dos pontos mais didaticos de RC e a divisao entre dinamica fixa e leitura treinavel.

        No projeto:

        - `W_in`, `W_res` e `b` sao inicializados aleatoriamente e mantidos fixos;
        - apenas o readout linear e ajustado com supervisao.

        Formalmente, o treinamento resolve

        $$
        W_{{out}}^* = \arg\min_{{W_{{out}}}}
        \|Y - \Phi W_{{out}}\|_2^2 + \lambda \|W_{{out}}\|_2^2,
        $$

        em que $\Phi$ e a matriz de features acumuladas ao longo do tempo e $\lambda$ e o hiperparametro de regularizacao Ridge.

        Essa escolha reduz o custo de treinamento em relacao a RNNs totalmente treinaveis e, ao mesmo tempo, preserva uma representacao temporal rica.

        ## 5. Como o tempo entra no modelo

        No projeto, o vetor de entrada sequencial e construido em `code/common/sequential_features.py` com sete componentes:

        - demanda previa normalizada;
        - promocao normalizada;
        - `dow_sin`, `dow_cos`;
        - `month_sin`, `month_cos`;
        - indicador de fim de semana.

        Em notacao compacta,

        $$
        u_t =
        \begin{{bmatrix}}
        \widetilde{{y}}_{{t-1}} &
        \widetilde{{p}}_t &
        \sin(2\pi \, \mathrm{{dow}}_t / 7) &
        \cos(2\pi \, \mathrm{{dow}}_t / 7) &
        \sin(2\pi \, \mathrm{{month}}_t / 12) &
        \cos(2\pi \, \mathrm{{month}}_t / 12) &
        \mathbb{{1}}_{{\mathrm{{weekend}}}}
        \end{{bmatrix}}^\top.
        $$

        Esse vetor coloca em uma mesma representacao:

        - memoria de curtissimo prazo, via $\widetilde{{y}}_{{t-1}}$;
        - contexto exogeno, via promocao;
        - ciclo temporal, via senos e cossenos.

        ## 6. O papel do washout

        Nos primeiros instantes da simulacao, o estado do reservatorio ainda esta fortemente contaminado pela inicializacao. Por isso, o projeto descarta os primeiros passos antes de treinar o readout.

        Se chamarmos o `washout` de $w$, o treino do readout usa apenas os tempos $t \ge w$:

        $$
        \Phi = [\phi_w, \phi_{{w+1}}, \dots, \phi_T]^\top.
        $$

        Em `fit_rc_readout()`, isso aparece no teste `if idx >= config.washout`.

        O `washout` nao e um detalhe de implementacao. Ele e uma parte conceitual do pipeline, porque separa a transiente inicial da dinamica que realmente queremos aproveitar.

        ## 7. Como o projeto implementa RC no caso Favorita

        A tabela abaixo resume o pipeline implementado.

        {dimensions_table}

        O fluxo completo do codigo e o seguinte:

        1. `build_scaler_state()` calcula medias e desvios para normalizacao;
        2. `scaled_input_vector()` constroi $u_t$;
        3. `EchoStateReservoir.step()` atualiza $x_t$;
        4. `_feature_vector()` monta $\phi_t = [1; u_t; x_t]$;
        5. `Ridge.fit()` estima o readout;
        6. `forecast_rc()` faz previsao recursiva no bloco de teste.

        O trecho central do treinamento e este:

        ```python
        input_vector = scaled_input_vector(prev_y, row, scaler=scaler)
        state = reservoir.step(input_vector)
        feature_rows.append(_feature_vector(state, input_vector))
        targets.append(float(row["y"]))
        ```

        Isso mostra a ideia central de RC em sua forma mais simples: o modelo nao aprende uma representacao temporal diretamente por backpropagation; ele coleta estados dinamicos e aprende apenas como le-los.

        ## 8. O que os artefatos intermediarios mostram

        O artigo nao precisa esperar a metrica final para ensinar alguma coisa. Os artefatos computacionais deste modulo mostram o pipeline em um nivel mais interno.

        {figure_block(results_name, "sequential_inputs_example.png", "Exemplo dos sinais de entrada sequenciais usados pelo RC.")}

        A imagem de entrada sequencial mostra que o reservatorio nao recebe apenas uma serie de vendas crua. Ele recebe uma codificacao temporal e exogena compacta.

        {figure_block(results_name, "rc_state_heatmap.png", "Heatmap dos estados internos do reservatorio classico no recorte adotado no Favorita.")}

        O heatmap dos estados ilustra duas ideias importantes:

        1. unidades diferentes respondem de modos diferentes ao mesmo estimulo;
        2. a memoria do reservatorio nao e um unico lag explicito, mas uma combinacao distribuida de estados.

        Em outras palavras, RC constroi uma base dinamica de features sem precisar enumerar manualmente toda a interacao temporal. Isso sustenta bem a **qualidade conceitual da representacao interna**, mas ainda nao diz, por si so, se a previsao final e forte.

        ## 9. Como avaliar a qualidade do RC sem misturar conceitos

        A avaliacao do RC fica mais clara quando separamos tres perguntas que muitas vezes sao misturadas.

        {evaluation_axes_table}

        Essa separacao evita um erro comum: tratar um heatmap interessante como prova suficiente de que a saida prevista e boa. Um estado interno pode ser didaticamente convincente e, ainda assim, produzir uma previsao final mediocre se o readout receber uma dinamica mal configurada.

        ## 10. Primeira evidencia quantitativa da saida do RC

        A tabela abaixo posiciona o RC default contra duas referencias honestas no mesmo bloco de teste de `90` dias.

        {quality_preview_table}

        Duas leituras importam aqui:

        1. o RC default funciona de ponta a ponta: ele gera previsoes finitas, mede erro e pode ser comparado sob o mesmo protocolo temporal;
        2. isso ainda nao basta para chama-lo de melhor solucao neste recorte: seu `MAE` ficou {rc_gap_vs_seasonal:.1f}\% acima do `Seasonal Naive` e {rc_gap_vs_ets:.1f}\% acima do `ETS`.

        Esse ponto e central para a honestidade cientifica do texto. O artigo agora nao apenas explica **como** o RC funciona; ele tambem mostra **o que a configuracao default entrega** quando confrontada com baselines serios.

        ## 11. Estabilidade experimental: a seed tambem faz parte da historia

        Um unico run pode dar uma impressao excessivamente otimista ou pessimista sobre RC. Por isso, executamos dez seeds para tres configuracoes simples.

        {stability_table}

        Tres fatos se destacam:

        1. a configuracao default apresentou alta variabilidade: `MAE` medio de {fmt(default_summary['mae_mean'])} com desvio-padrao de {fmt(default_summary['mae_std'])};
        2. no default, a faixa observada foi larga: de {fmt(default_summary['mae_min'])} ate {fmt(default_summary['mae_max'])};
        3. um ajuste simples para `spectral_radius = 0.20` e `leak_rate = 0.30` reduziu o `MAE` medio em {seed_mae_gain:.1f}\% e o desvio-padrao em {seed_std_gain:.1f}\% em relacao ao default.

        Esse resultado nao invalida o RC. Ele mostra algo mais util: o desempenho do reservatorio depende do regime dinamico em que ele opera. Em outras palavras, `seed` e hiperparametros fazem parte da qualidade experimental do modelo.

        ## 12. O que o washout realmente controla

        O `washout` decide quantos passos iniciais sao descartados antes de o readout ver os estados internos. Conceitualmente, ele separa transiente de inicializacao de dinamica util. Experimentalmente, ele muda o erro.

        {washout_table}

        Neste recorte, `washout = {best_washout['washout']}` foi o melhor valor entre os testados, com `MAE = {fmt(best_washout['mae'])}`. A licao pratica e simples:

        - `washout` muito curto pode contaminar o readout com estados ainda dominados pela inicializacao;
        - `washout` excessivo desperdica observacoes uteis de treino.

        ## 13. Como escolher os hiperparametros centrais sem adivinhar

        O leitor nao precisa decorar uma grade enorme de tuning para comecar. O mais importante e entender o papel de cada hiperparametro e que tipo de comportamento esperar quando ele varia.

        {hyperparameter_table}

        O ponto didatico aqui e decisivo: `spectral_radius`, `leak_rate`, `washout` e `n_reservoir` nao sao botoes arbitrarios. Eles controlam memoria, velocidade de resposta, uso do transiente e capacidade representacional.

        ## 14. O que este artigo ja prova, e o que ainda deixa em aberto

        ### 14.1 O que ja esta claro

        - a representacao interna do RC e boa como mecanismo conceitual: os estados sao heterogeneos, nao lineares e coerentes com a ideia de memoria distribuida;
        - a previsao final do RC e mensuravel e comparavel; portanto, o artigo ja nao depende apenas de intuicao;
        - a estabilidade experimental precisa ser reportada de forma explicita, porque a variacao por seed e relevante.

        ### 14.2 O que ainda nao esta encerrado

        - este artigo ainda nao fecha o benchmark completo da serie;
        - ele nao substitui uma comparacao ampla com `Prophet`, `XGBoost`, `LSTM` e `QRC`;
        - ele nao pretende vender o RC como melhor modelo neste recorte, e sim estabelecer uma base correta para julga-lo.

        Essa delimitacao melhora o artigo, porque troca promessa vaga por evidencia observavel.

        ## 15. Passo-a-passo para estudar ou modificar o RC do projeto

        Um leitor que queira estudar a implementacao deve seguir esta ordem:

        1. abrir `code/common/sequential_features.py`;
        2. verificar como o vetor `u_t` e construido;
        3. abrir `code/rc/model.py` e localizar `RCConfig`;
        4. ler `EchoStateReservoir.step()` junto da equacao do artigo;
        5. ler `fit_rc_readout()` e localizar o `washout`;
        6. executar `python code/rc/run.py`;
        7. validar o comportamento com `pytest code/rc/test_model.py`.

        Essa ordem importa. Se o leitor abrir apenas `run.py`, perde a correspondencia entre teoria e implementacao.

        ## 16. Conclusao

        RC agora esta formulado no contexto do projeto com um nivel maior de rigor. O artigo continua didatico, mas deixa de depender apenas de intuicao: ele mostra como o estado interno evolui, como a previsao sai do readout e como medir, de forma honesta, se essa saida e boa e estavel. A resposta correta para este recorte e clara: a representacao interna do RC e forte como objeto conceitual; a previsao final default e promissora, mas ainda inferior a baselines classicos fortes; e a estabilidade experimental exige cuidado com seed e hiperparametros. Isso prepara melhor o leitor para os artigos seguintes, porque o proximo passo deixa de ser "confiar no RC" e passa a ser "testar o RC com metodo".

        ## Entregaveis associados no repositorio

        - implementacao do RC: `code/rc/model.py`
        - execucao do RC: `code/rc/run.py`
        - testes do RC: `code/rc/test_model.py`
        - construcao de entrada sequencial: `code/common/sequential_features.py`
        - leitura quantitativa inicial: `{results_name}/rc_quality_preview.csv`
        - estabilidade em multiplas seeds: `{results_name}/rc_seed_stability_summary.csv`
        - sweep de `washout`: `{results_name}/rc_washout_sweep.csv`
        - artefatos deste artigo: `{results_name}/`

        ## Referencias

        - Jaeger, H. The "echo state" approach to analysing and training recurrent neural networks.
        - Lukosevicius, M.; Jaeger, H. Reservoir computing approaches to recurrent neural network training.
        - Lukosevicius, M. A practical guide to applying echo state networks.
        - Fujii, K.; Nakajima, K. Harnessing disordered-ensemble quantum dynamics for machine learning.
        """
    ).strip() + "\n"


def build_article_03(context: dict[str, dict]) -> str:
    ctx = context["03"]
    results_name = ctx["results_dir"].name
    metrics = {row["model"]: row for row in ctx["baseline_vs_rc"]}
    seasonal = metrics["Seasonal Naive"]
    rc = metrics["RC"]

    comparison_table = markdown_table(
        ["Modelo", "MAE", "RMSE", "WAPE", "sMAPE"],
        [
            [
                "Seasonal Naive",
                fmt(seasonal["mae"]),
                fmt(seasonal["rmse"]),
                fmt(seasonal["wape"], 4),
                fmt(seasonal["smape"], 4),
            ],
            [
                "RC",
                fmt(rc["mae"]),
                fmt(rc["rmse"]),
                fmt(rc["wape"], 4),
                fmt(rc["smape"], 4),
            ],
        ],
    )

    mae_gap = (float(rc["mae"]) / float(seasonal["mae"]) - 1.0) * 100.0
    rmse_gap = (float(rc["rmse"]) / float(seasonal["rmse"]) - 1.0) * 100.0

    return dedent(
        rf"""
        # Primeiro pipeline reproduzivel: previsao de demanda no Favorita com baselines e RC

        ## Resumo

        Este artigo transforma a teoria dos dois primeiros capitulos em um pipeline reproduzivel de previsao. O objetivo e ensinar o leitor a executar um baseline forte e um primeiro modelo de Reservoir Computing no mesmo recorte adotado no Favorita, medindo ambos com o mesmo protocolo temporal. Fazemos isso em modo passo-a-passo: carregamos a serie, separamos treino e teste, executamos `Seasonal Naive`, executamos RC, comparamos previsoes, interpretamos metricas e discutimos por que perder para um baseline nao invalida um experimento didatico. O resultado principal e honesto: no recorte inicial, `Seasonal Naive` supera o RC em todas as metricas, mas o RC funciona de ponta a ponta e abre as perguntas certas para os artigos seguintes.

        ## 1. O que o leitor vai aprender

        Ao final deste artigo, voce sera capaz de:

        1. executar um pipeline minimo de previsao no Favorita;
        2. usar `Seasonal Naive` como baseline serio, e nao apenas ilustrativo;
        3. rodar o RC classico do projeto do inicio ao fim;
        4. comparar previsoes com as mesmas metricas e o mesmo split temporal;
        5. interpretar um resultado inicial ruim como parte do processo cientifico.

        ## 2. O recorte experimental herdado

        Continuamos usando exatamente o mesmo recorte estabelecido no artigo 1:

        - `store_nbr = 1`
        - `family = BEVERAGES`
        - frequencia diaria
        - ultimos `90` dias como teste

        Isso significa que a comparacao deste artigo e justa por construcao. Ambos os modelos veem os mesmos dados e sao avaliados pelas mesmas metricas.

        ## 3. Passo 1: carregar a serie e separar treino e teste

        O pipeline comeca com as funcoes de `code/common/favorita.py`.

        ```python
        config = FavoritaSeriesConfig()
        frame = load_store_family_series(store_nbr=config.store_nbr, family=config.family)
        train, test = temporal_train_test_split(frame, test_days=config.test_days)
        ```

        Em notacao temporal, o experimento usa

        $$
        \mathcal{{D}}_{{train}} = \{{(x_t, y_t)\}}_{{t=1}}^{{T-90}},
        \qquad
        \mathcal{{D}}_{{test}} = \{{(x_t, y_t)\}}_{{t=T-89}}^T.
        $$

        Esse split e fundamental. Se ele mudar entre os modelos, a comparacao deixa de ser confiavel.

        ## 4. Passo 2: executar o baseline `Seasonal Naive`

        O baseline sazonal do projeto esta em `code/baselines/seasonal_naives/model.py` e implementa a regra

        $$
        \hat{{y}}_t = y_{{t-7}},
        $$

        usando sazonalidade semanal.

        A implementacao e curta exatamente porque sua funcao pedagogica e clara:

        ```python
        pattern = train["y"].to_numpy()[-season_length:]
        repeats = int(np.ceil(horizon / season_length))
        forecast = np.tile(pattern, repeats)[:horizon]
        ```

        Para executar:

        ```bash
        python code/baselines/seasonal_naives/run.py
        pytest code/baselines/seasonal_naives/test_model.py
        ```

        Um bom artigo de series temporais nao pula esta etapa. Se um modelo mais sofisticado nao supera esse baseline, isso precisa aparecer no texto.

        ## 5. Passo 3: executar o primeiro RC

        O RC classico do projeto esta em `code/rc/model.py` e usa a configuracao default:

        - `n_reservoir = 80`
        - `spectral_radius = 0.6`
        - `leak_rate = 0.15`
        - `washout = 14`

        A dinamica do reservatorio e

        $$
        x_t = (1 - \alpha) x_{{t-1}} + \alpha \tanh(W_{{res}} x_{{t-1}} + W_{{in}} u_t + b),
        $$

        e o readout resolve uma regressao Ridge sobre

        $$
        \phi_t = [1; u_t; x_t].
        $$

        Para executar:

        ```bash
        python code/rc/run.py
        pytest code/rc/test_model.py
        ```

        ## 6. Passo 4: medir com o mesmo protocolo

        As quatro metricas usadas na comparacao sao:

        $$
        \mathrm{{MAE}},\quad \mathrm{{RMSE}},\quad \mathrm{{WAPE}},\quad \mathrm{{sMAPE}}.
        $$

        O ponto metodologico aqui e simples, mas decisivo: os modelos precisam ser comparados no mesmo horizonte, com as mesmas observacoes de teste e as mesmas regras de previsao recursiva.

        ## 7. Resultados iniciais

        Os resultados reais obtidos no projeto foram os seguintes.

        {comparison_table}

        O `Seasonal Naive` supera o RC em todas as metricas. Em particular:

        - o `MAE` do RC ficou {mae_gap:.1f}% acima do baseline sazonal;
        - o `RMSE` do RC ficou {rmse_gap:.1f}% acima do baseline sazonal.

        {figure_block(results_name, "baseline_vs_rc_overlay.png", "Comparacao direta entre o baseline sazonal e o RC no bloco de teste.")}

        A sobreposicao das previsoes ajuda a ler o resultado com mais cuidado do que a tabela numerica isolada:

        - o baseline acompanha melhor o padrao semanal;
        - o RC funciona, mas ainda oscila mais em torno da serie observada;
        - o erro do RC nao vem de um colapso do pipeline, e sim de representacao insuficiente para este primeiro ajuste.

        ## 8. O que este experimento ensina

        O experimento e didaticamente valioso por quatro motivos.

        ### 8.1 Baseline forte nao e detalhe

        Em series temporais, um baseline sazonal simples pode ser surpreendentemente competitivo. Isso vale especialmente quando o sinal semanal e forte, como no caso de bebidas no recorte adotado no Favorita.

        ### 8.2 RC nao deve ser tratado como magia

        O RC funciona de ponta a ponta: carrega dados, constroi representacao, treina readout e produz previsoes. Mas funcionar nao e o mesmo que vencer. O artigo faz questao de manter essa distincao.

        ### 8.3 Reprodutibilidade e uma conquista em si

        Este pipeline deixa um trilho completo:

        - codigo de carregamento;
        - execucao do baseline;
        - execucao do RC;
        - testes;
        - metricas salvas;
        - imagens comparativas.

        Essa cadeia e o que permite que os artigos seguintes falem de tuning, avaliacao justa e QRC sem perder a base experimental.

        ### 8.4 Derrota inicial organiza as proximas perguntas

        Como o RC perdeu para o baseline, os artigos seguintes precisam responder:

        - o tamanho do reservatorio esta adequado?
        - a memoria do modelo esta curta ou longa demais?
        - o raio espectral esta instavel?
        - o leak rate esta ajudando ou atrapalhando?

        Em um bom percurso didatico, resultados fracos produzem perguntas fortes.

        ## 9. Como este artigo se conecta ao benchmark maior

        O experimento deste artigo nao encerra a comparacao. Ele apenas estabelece o primeiro patamar:

        - `Seasonal Naive` sera mantido como referencia;
        - RC sera refinado e estudado com mais detalhe;
        - novos competidores entrarao depois: `ETS`, `Prophet`, `XGBoost`, `LSTM` e `QRC`.

        Essa progressao e importante porque impede um salto artificial do "primeiro RC" diretamente para o "QRC final".

        ## 10. Conclusao

        O primeiro pipeline reproduzivel da serie esta fechado. O baseline sazonal venceu, o RC funcionou sem vencer e o leitor ja tem um experimento concreto para estudar, modificar e rerodar. Isso e exatamente o que um artigo didatico deveria entregar neste ponto: menos promessas vagas e mais reproducao concreta.

        O proximo artigo vai usar essa base para explicar por que RC pode melhorar ou piorar tanto quando seus hiperparametros mudam.

        ## Entregaveis associados no repositorio

        - baseline sazonal: `code/baselines/seasonal_naives/`
        - RC classico: `code/rc/`
        - comparacao numerica e visual deste artigo: `{results_name}/`
        - figuras principais: `baseline_vs_rc_overlay.png`, `seasonal_naive_forecast_plot.png`, `rc_forecast_plot.png`

        ## Referencias

        - Hyndman, R. J.; Athanasopoulos, G. Forecasting: Principles and Practice.
        - Jaeger, H. The "echo state" approach to analysing and training recurrent neural networks.
        - Lukosevicius, M. A practical guide to applying echo state networks.
        """
    ).strip() + "\n"


def build_article_04(context: dict[str, dict]) -> str:
    ctx = context["04"]
    results_name = ctx["results_dir"].name

    table_n = markdown_table(
        ["n_reservoir", "MAE", "RMSE", "WAPE", "sMAPE"],
        [
            [
                row["value"],
                fmt(row["mae"]),
                fmt(row["rmse"]),
                fmt(row["wape"], 4),
                fmt(row["smape"], 4),
            ]
            for row in ctx["sweep_n_reservoir"]
        ],
    )
    table_radius = markdown_table(
        ["spectral_radius", "MAE", "RMSE", "WAPE", "sMAPE"],
        [
            [
                row["value"],
                fmt(row["mae"]),
                fmt(row["rmse"]),
                fmt(row["wape"], 4),
                fmt(row["smape"], 4),
            ]
            for row in ctx["sweep_spectral_radius"]
        ],
    )
    table_leak = markdown_table(
        ["leak_rate", "MAE", "RMSE", "WAPE", "sMAPE"],
        [
            [
                row["value"],
                fmt(row["mae"]),
                fmt(row["rmse"]),
                fmt(row["wape"], 4),
                fmt(row["smape"], 4),
            ]
            for row in ctx["sweep_leak_rate"]
        ],
    )

    return dedent(
        rf"""
        # Por que Reservoir Computing funciona: memoria, nao linearidade e capacidade de representacao

        ## Resumo

        Este artigo responde a pergunta que ficou aberta depois do primeiro pipeline: por que o desempenho do RC muda tanto quando ajustamos seus hiperparametros? Para responder, conectamos memoria, nao linearidade e capacidade de representacao a resultados computacionais reais do projeto. Comecamos por uma leitura teorica do reservatorio, mostramos como o `leak_rate` controla a escala temporal efetiva, como o `spectral_radius` influencia estabilidade e mistura e como o tamanho do reservatorio afeta a base de representacao. Em seguida, analisamos os resultados de varreduras reais sobre `n_reservoir`, `spectral_radius` e `leak_rate`. O artigo nao apenas explica RC em abstrato: ele mostra o que essas ideias produzem, ou destroem, no recorte adotado no Favorita.

        ## 1. O que o leitor vai aprender

        Ao final deste artigo, voce sera capaz de:

        1. explicar memoria e nao linearidade no RC em termos matematicos;
        2. entender por que `spectral_radius` e `leak_rate` mudam o comportamento do modelo;
        3. interpretar tabelas de tuning do RC;
        4. diferenciar capacidade de representacao de mera quantidade de unidades;
        5. decidir o que vale testar antes de partir para QRC.

        ## 2. Memoria: o passado precisa continuar presente

        Em RC, a memoria nao aparece como um vetor de lags explicitamente escrito. Ela aparece no proprio estado do reservatorio. Se linearizarmos a dinamica em torno de uma regiao pequena, obtemos aproximadamente

        $$
        x_t \approx A x_{{t-1}} + \alpha W_{{in}} u_t + \alpha b,
        \qquad
        A = (1 - \alpha) I + \alpha W_{{res}}.
        $$

        Desdobrando a recursao:

        $$
        x_t \approx \sum_{{k=0}}^\infty A^k (\alpha W_{{in}} u_{{t-k}} + \alpha b).
        $$

        Essa expressao mostra a intuicao correta: o estado atual e uma superposicao ponderada do passado. A velocidade com que o passado "desaparece" depende da matriz efetiva $A$, logo depende de `spectral_radius` e `leak_rate`.

        ### 2.1 O papel do leak rate

        O `leak_rate` regula quanto do estado novo substitui o estado antigo. Valores pequenos alongam a memoria; valores grandes tornam a resposta mais reativa.

        No projeto, o `leak_rate` default foi `0.15`, mas a varredura mostrou que `0.30` melhora levemente o resultado neste recorte.

        {table_leak}

        Esse resultado ensina uma licao importante: uma memoria mais longa nao e automaticamente melhor. Se a serie responde fortemente a promocao e sazonalidade semanal, uma resposta um pouco mais rapida pode ajudar.

        ### 2.2 O papel do washout

        O `washout` separa o regime transiente inicial da dinamica util para treino:

        $$
        \Phi = [\phi_w, \phi_{{w+1}}, \dots, \phi_T]^\top.
        $$

        Sem `washout`, o readout pode aprender artefatos de inicializacao em vez de aprender uma representacao estabilizada da serie.

        ## 3. Nao linearidade: por que a serie nao cabe em uma regra unica

        O reservatorio usa a nao linearidade `tanh`:

        $$
        \widetilde{{x}}_t = \tanh(W_{{res}} x_{{t-1}} + W_{{in}} u_t + b).
        $$

        Essa nao linearidade e o que permite ao modelo misturar efeitos de calendario, promocao e demanda previa sem impor uma relacao puramente aditiva ou puramente linear.

        Em previsao de demanda, isso importa porque:

        - a mesma promocao pode gerar efeitos diferentes em dias diferentes;
        - o mesmo dia da semana pode ter resposta diferente dependendo do historico imediato;
        - a relacao entre passado e presente nao precisa ser monotona nem linear.

        ## 4. Capacidade de representacao: tamanho importa, mas nao sozinho

        Um erro comum de iniciantes e supor que "mais unidades" sempre significa "mais desempenho". A varredura de `n_reservoir` no projeto mostra o contrario.

        {table_n}

        A configuracao `n_reservoir = 80` foi a melhor entre as testadas. Quando o reservatorio ficou pequeno demais (`40`), o erro explodiu. Mas aumentar para `120` e `160` tambem piorou.

        Esse comportamento sugere que capacidade util e compatibilidade com o problema importam mais do que simplesmente aumentar a dimensionalidade.

        ## 5. Estabilidade e mistura: o papel do spectral radius

        O `spectral_radius` reescala a matriz recorrente para controlar o quanto a dinamica interna amplifica ou dissipa o estado.

        {table_radius}

        A varredura mostra tres regimes didaticamente importantes:

        1. `0.2` produziu o melhor conjunto de metricas entre os valores testados;
        2. `0.6` ficou em uma faixa intermediaria e foi o default do primeiro pipeline;
        3. `0.8` e `1.0` degradaram muito a estabilidade, com explosao de erro.

        Em outras palavras, este recorte prefere um reservatorio mais contido do que o default inicial sugeria.

        ## 6. Como ler os hiperparametros do RC no codigo

        O ponto de entrada do tuning esta em `RCConfig`:

        ```python
        @dataclass(frozen=True)
        class RCConfig:
            n_reservoir: int = 80
            spectral_radius: float = 0.6
            leak_rate: float = 0.15
            input_scale: float = 0.8
            bias_scale: float = 0.1
            washout: int = 14
            ridge_alpha: float = 1e-3
            seed: int = 7
        ```

        Um modo pratico de estudar o modelo e variar apenas um hiperparametro por vez, mantendo os demais fixos. Foi exatamente isso que os artefatos deste artigo fizeram.

        ## 7. O que o resultado atual do RC sugere

        {figure_block(results_name, "rc_sensitivity_summary.png", "Resumo visual das varreduras de hiperparametros do RC no recorte adotado no Favorita.")}

        O resumo visual permite uma leitura didatica direta:

        - o modelo e sensivel ao `spectral_radius`;
        - o `leak_rate` possui um ponto intermediario util;
        - o tamanho do reservatorio tem um regime otimo local, e nao monotonia.

        Isso confirma uma licao central para a serie: o RC nao deve ser avaliado apenas por uma configuracao arbitraria. Seu desempenho depende de como ajustamos memoria, mistura e capacidade.

        ## 8. O que RC faz bem e o que ainda nao faz bem aqui

        ### 8.1 O que RC faz bem

        - constroi uma representacao temporal dinamica de baixo custo de treinamento;
        - absorve sinais de promocao e calendario sem uma engenharia tabular extensa;
        - oferece uma ponte conceitual excelente para o QRC.

        ### 8.2 O que RC ainda nao faz bem aqui

        - ainda nao supera os melhores modelos classicos neste recorte;
        - ainda depende de tuning cuidadoso para evitar instabilidade ou sub-representacao;
        - ainda nao incorpora a riqueza completa do dataset Favorita.

        ## 9. Passo-a-passo para reproduzir o estudo de sensibilidade

        Um leitor que queira repetir este artigo pode seguir esta sequencia:

        1. executar `python code/rc/run.py` para fixar a configuracao base;
        2. alterar `RCConfig` em `code/rc/model.py` ou criar instancias novas em um script de experimento;
        3. rerodar a previsao para cada combinacao;
        4. comparar `MAE`, `RMSE`, `WAPE` e `sMAPE`;
        5. guardar o resultado em CSV e imagem, como foi feito em `{results_name}/`.

        Esse processo prepara o leitor para a fase seguinte da serie, em que a comparacao deixa de ser apenas "baseline versus RC" e vira um benchmark mais amplo.

        ## 10. Conclusao

        Este artigo mostrou que o RC funciona porque oferece memoria distribuida e nao linearidade controlada, mas que essa vantagem depende de como configuramos o sistema dinamico. O proprio comportamento das varreduras do projeto ensina essa licao melhor do que qualquer definicao abstrata: parametros inadequados destroem o desempenho, enquanto escolhas razoaveis tornam o reservatorio competitivo o suficiente para merecer comparacao seria.

        ## Entregaveis associados no repositorio

        - implementacao do RC: `code/rc/model.py`
        - artefatos de sensibilidade: `{results_name}/`
        - arquivos principais: `rc_sweep_n_reservoir.csv`, `rc_sweep_spectral_radius.csv`, `rc_sweep_leak_rate.csv`, `rc_sensitivity_summary.png`

        ## Referencias

        - Jaeger, H. The "echo state" approach to analysing and training recurrent neural networks.
        - Lukosevicius, M. A practical guide to applying echo state networks.
        - Verstraeten, D. et al. Memory versus non-linearity in reservoirs.
        """
    ).strip() + "\n"


def build_article_05(context: dict[str, dict]) -> str:
    ctx = context["05"]
    results_name = ctx["results_dir"].name
    benchmark_metrics = ctx["benchmark_metrics"]
    benchmark_ranked = ctx["benchmark_ranked"]

    benchmark_table = markdown_table(
        ["Modelo", "Familia", "MAE", "RMSE", "WAPE", "sMAPE"],
        [
            [
                row["model"],
                row["family"],
                fmt(row["mae"]),
                fmt(row["rmse"]),
                fmt(row["wape"], 4),
                fmt(row["smape"], 4),
            ]
            for row in benchmark_metrics
        ],
    )

    ranked_table = markdown_table(
        ["Modelo", "Rank medio", "MAE", "RMSE", "WAPE", "sMAPE"],
        [
            [
                row["model"],
                fmt(row["avg_rank"], 2),
                fmt(row["mae"]),
                fmt(row["rmse"]),
                fmt(row["wape"], 4),
                fmt(row["smape"], 4),
            ]
            for row in benchmark_ranked
        ],
    )

    implementation_table = dedent(
        r"""
        ```{=latex}
        \begin{table}[htbp]
        \centering
        \small
        \begin{tabularx}{\linewidth}{@{}lYY@{}}
        \toprule
        Modelo & Implementacao & Ideia central \\
        \midrule
        Seasonal Naive & \path{code/baselines/seasonal_naives/} & repete a ultima semana observada \\
        ETS & \path{code/baselines/ets/} & modelo de nivel, tendencia e sazonalidade aditiva \\
        Prophet & \path{code/baselines/prophet/} & decomposicao de tendencia, sazonalidade e regressor exogeno \\
        XGBoost & \path{code/classical/xgboost/} & aprendizado tabular sobre lags e medias moveis \\
        LSTM & \path{code/classical/lstm/} & rede recorrente treinada por gradiente \\
        RC & \path{code/rc/} & reservatorio fixo e readout linear \\
        QRC & \path{code/qrc/} & reservatorio quantico implementado com Qiskit \\
        \bottomrule
        \end{tabularx}
        \end{table}
        ```
        """
    ).strip()

    return dedent(
        rf"""
        # Avaliacao justa em previsao de demanda: baselines, IA classica e Reservoir Computing

        ## Resumo

        Este artigo organiza o benchmark central da serie. O objetivo nao e apenas mostrar uma tabela final, mas ensinar como comparar modelos de series temporais de forma justa quando o interesse e chegar ate RC e QRC sem perder contato com tecnicas classicas fortes. Por isso, o texto formaliza o protocolo experimental, resume as implementacoes ja construidas no projeto, apresenta as equacoes minimas das familias avaliadas e discute o benchmark consolidado real no recorte adotado no Favorita. O resultado mais importante e metodologico: `ETS`, `XGBoost` e `Prophet` formam uma referencia forte que impede avaliar RC e QRC contra baselines fracos.

        ## 1. O que o leitor vai aprender

        Ao final deste artigo, voce sera capaz de:

        1. comparar modelos temporais com um protocolo realmente comum;
        2. entender o papel de cada familia de modelo no benchmark;
        3. ler uma tabela comparativa sem cair em conclusoes apressadas;
        4. reproduzir o benchmark com os scripts do projeto;
        5. usar os resultados classicos como referencia seria para RC e QRC.

        ## 2. Por que avaliacao em series temporais e delicada

        Em series temporais, avaliacao injusta aparece facilmente:

        - quando um modelo usa um split temporal diferente;
        - quando features usam informacao do futuro;
        - quando um modelo recebe regressoras exogenas e outro nao;
        - quando os horizontes de previsao nao coincidem;
        - quando as metricas destacadas mudam de um experimento para outro.

        Para evitar isso, este projeto fixa o seguinte principio:

        $$
        \text{{mesmo recorte}} + \text{{mesmo split}} + \text{{mesmas metricas}} = \text{{comparacao honesta}}.
        $$

        ## 3. Protocolo experimental da serie

        ### 3.1 Recorte comum

        Todos os modelos usam:

        - `store_nbr = 1`
        - `family = BEVERAGES`
        - frequencia diaria
        - ultimos `90` dias como teste

        ### 3.2 Regra de split

        Formalmente:

        $$
        \mathcal{{D}}_{{train}} = \{{(x_t, y_t)\}}_{{t=1}}^{{T-90}},
        \qquad
        \mathcal{{D}}_{{test}} = \{{(x_t, y_t)\}}_{{t=T-89}}^T.
        $$

        ### 3.3 Modelos avaliados

        {implementation_table}

        ### 3.4 Metricas avaliadas

        O benchmark usa:

        $$
        \mathrm{{MAE}},\ \mathrm{{RMSE}},\ \mathrm{{WAPE}},\ \mathrm{{sMAPE}}.
        $$

        As implementacoes dessas metricas estao em `code/common/metrics.py`.

        ## 4. As familias de modelo em uma pagina

        Para manter a comparacao didatica, vale resumir a logica de cada familia.

        ### 4.1 Seasonal Naive

        $$
        \hat{{y}}_t = y_{{t-7}}.
        $$

        Serve como baseline sazonal minimo.

        ### 4.2 ETS

        O ETS aditivo pode ser resumido por

        $$
        \ell_t = \alpha (y_t - s_{{t-m}}) + (1 - \alpha)(\ell_{{t-1}} + b_{{t-1}}),
        $$
        $$
        b_t = \beta (\ell_t - \ell_{{t-1}}) + (1 - \beta) b_{{t-1}},
        $$
        $$
        s_t = \gamma (y_t - \ell_t) + (1 - \gamma) s_{{t-m}}.
        $$

        ### 4.3 Prophet

        O Prophet modela a serie como

        $$
        y(t) = g(t) + s(t) + h(t) + \beta x_t + \epsilon_t,
        $$

        em que `onpromotion` entra como regressor exogeno no projeto.

        ### 4.4 XGBoost

        O modelo tabular usa lags, medias moveis e calendario para aprender

        $$
        \hat{{y}}_t = \sum_{{m=1}}^M f_m(z_t),
        $$

        com $z_t$ contendo `lag_1`, `lag_7`, `lag_14`, `lag_28`, medias moveis e calendarios.

        ### 4.5 LSTM

        A LSTM usa portas para atualizar memoria:

        $$
        i_t = \sigma(W_i [h_{{t-1}}, x_t] + b_i), \quad
        f_t = \sigma(W_f [h_{{t-1}}, x_t] + b_f),
        $$
        $$
        c_t = f_t \odot c_{{t-1}} + i_t \odot \tilde{{c}}_t.
        $$

        ### 4.6 RC

        $$
        x_t = (1 - \alpha) x_{{t-1}} + \alpha \tanh(W_{{res}} x_{{t-1}} + W_{{in}} u_t + b).
        $$

        ### 4.7 QRC

        O QRC sera detalhado nos artigos 6 e 7, mas aqui ele entra como

        $$
        z_t^{{(j)}} = \langle \psi_t | O_j | \psi_t \rangle,
        \qquad
        \hat{{y}}_t = W_{{out}} [1; u_t; z_t].
        $$

        ## 5. Benchmark comparativo atual

        A tabela abaixo resume os resultados reais obtidos no projeto.

        {benchmark_table}

        Uma leitura ordenada por rank medio reforca a comparacao.

        {ranked_table}

        {figure_block(results_name, "benchmark_metric_bars.png", "Comparacao visual das metricas do benchmark completo.")}

        {figure_block(results_name, "benchmark_forecast_grid.png", "Grade de previsoes dos diferentes modelos no mesmo bloco de teste.")}

        ## 6. Leitura dos resultados

        ### 6.1 ETS na lideranca

        O `ETS` foi o melhor modelo no recorte em todas as metricas principais. Isso e importante porque mostra que um baseline estatistico bem implementado continua sendo uma referencia dificil de bater.

        ### 6.2 XGBoost e Prophet como faixa intermediaria forte

        `XGBoost` e `Prophet` formam uma segunda faixa de desempenho. Ambos ficaram muito proximos do `Seasonal Naive` em algumas metricas, mas entregaram um pacote mais robusto no conjunto do benchmark.

        ### 6.3 O que o RC entrega

        O `RC` superou a `LSTM`, o que e pedagogicamente interessante. Em um setup pequeno e pouco ajustado, uma rede recorrente treinada por gradiente nao vence automaticamente um reservatorio fixo.

        ### 6.4 O que o QRC entrega

        O `QRC` funcionou de ponta a ponta e foi comparado no mesmo recorte de dados. No entanto, ficou abaixo das tecnicas classicas neste benchmark. Isso nao invalida o estudo; ao contrario, torna a comparacao mais honesta.

        ## 7. O que significa uma comparacao justa

        Este benchmark so e didaticamente util porque respeita tres regras:

        1. todos os modelos usam os mesmos dados;
        2. todos produzem previsao para os mesmos `90` dias;
        3. todos sao julgados pelas mesmas metricas.

        Isso evita a narrativa enganosa de que um modelo "venceu" porque recebeu mais contexto ou uma tarefa mais facil.

        ## 8. Passo-a-passo para reproduzir o benchmark

        A reproducao pode ser feita em lotes, executando um script por familia:

        ```bash
        python code/baselines/seasonal_naives/run.py
        python code/baselines/ets/run.py
        python code/baselines/prophet/run.py
        python code/classical/xgboost/run.py
        python code/classical/lstm/run.py
        python code/rc/run.py
        python code/qrc/run.py
        ```

        Os testes associados seguem a mesma organizacao:

        ```bash
        pytest code/baselines/seasonal_naives/test_model.py
        pytest code/baselines/ets/test_model.py
        pytest code/baselines/prophet/test_model.py
        pytest code/classical/xgboost/test_model.py
        pytest code/classical/lstm/test_model.py
        pytest code/rc/test_model.py
        pytest code/qrc/test_model.py
        pytest code/qrc/test_objective.py
        ```

        ## 9. Checklist de boas praticas

        O artigo deixa um checklist minimo para os proximos experimentos:

        - manter o split temporal fixo;
        - registrar metricas em arquivo;
        - salvar previsoes e figuras;
        - documentar hiperparametros;
        - nao comparar RC e QRC apenas com baselines fracos.

        ## 10. Regras herdadas para a fase QRC

        Quando chegarmos ao QRC, duas regras deste benchmark continuam valendo:

        1. o QRC deve ser comparado com as tecnicas classicas ja implementadas;
        2. o mesmo recorte de dados deve ser mantido, mesmo que o reservatorio quantico simplifique sua representacao interna.

        Isso e o que transforma o estudo final em um artigo de ensino serio, e nao em uma demonstracao isolada.

        ## 11. Conclusao

        O benchmark consolidado da serie esta agora estabelecido. Ele mostra que a competicao relevante para RC e QRC nao e contra referencias artificiais, mas contra modelos classicos fortes e bem executados. Isso torna a rota ate QRC intelectualmente mais exigente, mas tambem muito mais valiosa.

        ## Entregaveis associados no repositorio

        - benchmark consolidado: `code/RESULTS.md`
        - implementacoes de baseline: `code/baselines/`
        - implementacoes classicas: `code/classical/`
        - implementacao de RC: `code/rc/`
        - implementacao de QRC: `code/qrc/`
        - artefatos comparativos deste artigo: pasta `computational_results_*/`

        ## Referencias

        - Hyndman, R. J.; Athanasopoulos, G. Forecasting: Principles and Practice.
        - Taylor, S. J.; Letham, B. Forecasting at Scale.
        - Chen, T.; Guestrin, C. XGBoost: A scalable tree boosting system.
        - Hochreiter, S.; Schmidhuber, J. Long short-term memory.
        - Jaeger, H. The "echo state" approach to analysing and training recurrent neural networks.
        """
    ).strip() + "\n"


def build_article_06(context: dict[str, dict]) -> str:
    ctx = context["06"]
    results_name = ctx["results_dir"].name
    focus_summary = ctx["qrc_focus_summary"]
    best_objective = ctx["qrc_best_objective"]
    best_extended = ctx["qrc_best_extended"]

    top_rows = []
    for row in focus_summary[:5]:
        top_rows.append(
            [
                row["n_qubits"],
                row["window"],
                fmt(row["mean_mae"]),
                fmt(row["mean_rmse"]),
                fmt(row["mean_wape"], 4),
                fmt(row["mean_smape"], 4),
                fmt(row["avg_rank"], 2),
            ]
        )
    focus_table_rows = "\n".join(
        f'{row[0]} & {row[1]} & {row[2]} & {row[3]} & {row[4]} & {row[5]} & {row[6]} \\\\'
        for row in top_rows
    )
    focus_table = dedent(
        rf"""
        ```{{=latex}}
        \begin{{table}}[htbp]
        \centering
        \footnotesize
        \setlength{{\tabcolsep}}{{3pt}}
        \begin{{tabularx}}{{\linewidth}}{{@{{}}llCCCCC@{{}}}}
        \toprule
        Qubits & Window & \shortstack{{MAE\\medio}} & \shortstack{{RMSE\\medio}} & \shortstack{{WAPE\\medio}} & \shortstack{{sMAPE\\medio}} & \shortstack{{Rank\\medio}} \\
        \midrule
        {focus_table_rows}
        \bottomrule
        \end{{tabularx}}
        \end{{table}}
        ```
        """
    ).strip()

    objective_table = markdown_table(
        ["Criterio", "Melhor configuracao", "Valor"],
        [
            [
                "Melhor rank medio multi-metrica",
                f'{best_extended["best"]["n_qubits"]}x{best_extended["best"]["window"]}',
                fmt(best_extended["best"]["avg_rank"], 2),
            ],
            [
                "Melhor funcao objetivo escalar",
                f'{best_objective["best"]["n_qubits"]}x{best_objective["best"]["window"]}',
                fmt(best_objective["best"]["objective_score"], 4),
            ],
        ],
    )

    objective_config = best_objective["objective_config"]
    weights = {
        "mae": objective_config["mae_weight"],
        "rmse": objective_config["rmse_weight"],
        "wape": objective_config["wape_weight"],
        "smape": objective_config["smape_weight"],
    }
    complexity_weight = objective_config["complexity_weight"]

    return dedent(
        rf"""
        # De Reservoir Computing classico a Quantum Reservoir Computing: a ponte conceitual

        ## Resumo

        Este artigo constroi a ponte entre o RC classico estudado ate aqui e o QRC usado no estudo final. O objetivo e mostrar que QRC nao nasce como um tema separado do restante da obra, mas como uma extensao natural da ideia de reservatorio: manter a separacao entre dinamica rica e readout simples, trocando o meio classico por um meio quantico. O texto apresenta o paralelo formal entre RC e QRC, mapeia essa ponte para a implementacao em Qiskit, discute a estrategia de tuning usada no projeto e introduz a funcao objetivo que equilibra desempenho e complexidade (`qubits`, `window`). Ao final, o leitor sabe por que duas configuracoes candidatas emergiram do tuning: `14x7` como melhor ponto multi-metrica e `8x5` como melhor compromisso segundo a funcao objetivo escalar.

        ## 1. O que o leitor vai aprender

        Ao final deste artigo, voce sera capaz de:

        1. enxergar RC e QRC dentro do mesmo paradigma;
        2. entender como entradas classicas sao codificadas em circuitos quanticos;
        3. ler a implementacao do QRC em `code/qrc/model.py`;
        4. interpretar o tuning de `n_qubits` e `window`;
        5. justificar tecnicamente por que `14x7` e `8x5` foram preservados para o artigo final.

        ## 2. RC como paradigma geral

        No RC classico, a ideia e:

        $$
        u_t \longrightarrow x_t \longrightarrow \phi_t \longrightarrow \hat{{y}}_t.
        $$

        Em outras palavras:

        - a entrada $u_t$ perturba um sistema dinamico;
        - o sistema responde com um estado $x_t$;
        - o readout linear aprende a ler esse estado.

        O QRC preserva exatamente essa logica. O que muda e o meio em que a dinamica interna acontece.

        ## 3. O salto para o quantico

        No projeto, o reservatorio quantico usa circuitos de reuploading implementados com Qiskit. Para cada qubit $q$ e para cada passo de entrada, a codificacao usa angulos do tipo

        $$
        \theta^{{(q,t)}}_x = s \, w_{{x,q}}^\top u_t + b_q,
        \qquad
        \theta^{{(q,t)}}_y = s \, w_{{y,q}}^\top u_t,
        $$

        em que:

        - $u_t \in \mathbb{{R}}^4$ e o vetor classico reduzido;
        - $s$ e `input_scale`;
        - $w_{{x,q}}$ e $w_{{y,q}}$ sao pesos aleatorios por qubit.

        O circuito elementar do projeto aplica:

        1. `RX` e `RY` em cada qubit;
        2. um anel de emaranhamento `CZ`;
        3. rotacoes `RZ` apos cada acoplamento.

        ## 4. Paralelo direto entre RC e QRC

        O paralelo conceitual entre os dois modelos pode ser escrito assim:

        | RC classico | QRC do projeto |
        | --- | --- |
        | estado vetorial $x_t$ | estado quantico $\lvert\psi_t\rangle$ |
        | matriz recorrente $W_{{res}}$ | circuito com `RX`, `RY`, `CZ`, `RZ` |
        | features $[1; u_t; x_t]$ | features $[1; u_t; z_t]$ |
        | readout linear | readout linear |

        No QRC, as features observadas sao expectativas de operadores:

        $$
        z_t^{{(j)}} = \langle \psi_t | O_j | \psi_t \rangle.
        $$

        No projeto, cada configuracao com $n_{{\text{{qubits}}}} = q$ gera $3q$ observaveis:

        - $q$ observaveis $Z$;
        - $q$ observaveis $X$;
        - $q$ observaveis $ZZ$ entre vizinhos.

        Isso significa que:

        - `8x5` usa $24$ observaveis e um vetor final com $1 + 4 + 24 = 29$ features;
        - `14x7` usa $42$ observaveis e um vetor final com $1 + 4 + 42 = 47$ features.

        ## 5. Como o projeto implementa essa ponte em Qiskit

        O passo central de codificacao esta em `_step_circuit()`:

        ```python
        for q in range(self.config.n_qubits):
            angle_x = self.config.input_scale * float(self.rx_weights[q] @ input_vector) + self.bias[q]
            angle_y = self.config.input_scale * float(self.ry_weights[q] @ input_vector)
            circuit.rx(angle_x, q)
            circuit.ry(angle_y, q)
        ```

        O emaranhamento em anel aparece logo em seguida:

        ```python
        for q in range(self.config.n_qubits - 1):
            circuit.cz(q, q + 1)
            circuit.rz(self.entangling_angles[q], q + 1)
        circuit.cz(self.config.n_qubits - 1, 0)
        circuit.rz(self.entangling_angles[-1], 0)
        ```

        E as features sao extraidas via `Statevector.expectation_value()`:

        ```python
        state = Statevector.from_instruction(circuit)
        features = [float(np.real(state.expectation_value(obs))) for obs in self.observables]
        ```

        Essa implementacao e importante pedagogicamente porque mostra que o QRC do projeto nao e uma caixa preta: ele e um pipeline legivel, curto e comparavel ao RC classico.

        ## 6. Tuning de qubits e window

        O tuning focalizado do projeto produziu a seguinte faixa superior de configuracoes:

        {focus_table}

        {figure_block(results_name, "qrc_tuning_heatmap.png", "Mapa de calor do tuning de qubits e window para o QRC.")}

        A tabela mostra uma licao decisiva: aumentar `n_qubits` e `window` nao melhora automaticamente o desempenho. O melhor ponto robusto ficou em `14x7`, enquanto `16x5` e `16x7` pioraram o rank medio.

        ## 7. Uma funcao objetivo para escolher configuracoes comparaveis

        O projeto nao ficou preso a um unico criterio. Alem do rank medio multi-metrica, foi proposta uma funcao objetivo escalar

        $$
        J(q, w) = G(q, w) \cdot C(q, w),
        $$

        com

        $$
        G(q, w) = \exp\left(\sum_k \omega_k \log\frac{{m_k(q, w)}}{{r_k}}\right),
        $$

        e

        $$
        C(q, w) = 1 + \lambda \, \frac{{\mathrm{{norm}}(q) + \mathrm{{norm}}(w)}}{{2}}.
        $$

        Aqui:

        - $m_k(q, w)$ sao as metricas do QRC;
        - $r_k$ sao as metricas da melhor referencia nao-QRC;
        - $\omega_k$ sao pesos por metrica;
        - $\lambda = {complexity_weight}$ penaliza complexidade adicional.

        Os pesos usados foram:

        - `MAE = {weights["mae"]}`
        - `RMSE = {weights["rmse"]}`
        - `WAPE = {weights["wape"]}`
        - `sMAPE = {weights["smape"]}`

        O resumo da selecao ficou assim:

        {objective_table}

        O criterio multi-metrica favorece `14x7`. A funcao objetivo penalizada favorece `8x5`.

        ## 8. O que se ganha e o que se perde na ponte para QRC

        ### 8.1 O que se ganha

        - uma nova classe de dinamica para representar series temporais;
        - uma formulacao muito natural para discutir observaveis e mistura de estados;
        - uma extensao conceitual elegante do paradigma de reservatorio.

        ### 8.2 O que se perde

        - simplicidade operacional em relacao ao RC classico;
        - custo computacional, especialmente quando `qubits` e `window` crescem;
        - interpretabilidade imediata do estado interno.

        ## 9. Por que o benchmark anterior precisa ser herdado

        O QRC so faz sentido pedagogico neste projeto porque herda o benchmark do artigo 5. Sem esse benchmark, seria facil tratar o QRC como curiosidade isolada. Com ele, o leitor entende exatamente contra o que o QRC precisa ser comparado:

        - `ETS`
        - `XGBoost`
        - `Prophet`
        - `Seasonal Naive`
        - `RC`
        - `LSTM`

        Essa heranca metodologica e o que impede a fase quantica de perder contato com o problema de negocio.

        ## 10. Conclusao

        A ponte entre RC classico e QRC esta pronta. O leitor agora tem um mapa formal, implementacional e experimental do salto para o quantico. O artigo final vai aproveitar exatamente essa ponte para executar e interpretar o QRC no recorte adotado no Favorita, comparando `14x7`, `8x5` e os melhores modelos classicos.

        ## Entregaveis associados no repositorio

        - implementacao do QRC: `code/qrc/model.py`
        - funcao objetivo: `code/qrc/objective.py`
        - documentacao da funcao objetivo: `code/qrc/OBJECTIVE.md`
        - artefatos deste artigo: `{results_name}/`

        ## Referencias

        - Fujii, K.; Nakajima, K. Harnessing disordered-ensemble quantum dynamics for machine learning.
        - Ghosh, S. et al. Quantum reservoir processing.
        - Qiskit documentation.
        - Monzani, F.; Ricci, E.; Nigro, L.; Prati, E. QRC-Lab: An Educational Toolbox for Quantum Reservoir Computing. arXiv:2602.03522.
        """
    ).strip() + "\n"


def build_article_07(context: dict[str, dict]) -> str:
    ctx = context["07"]
    results_name = ctx["results_dir"].name
    focus_rows = {row["model"]: row for row in ctx["qrc_focus_comparison"]}
    qrc14 = focus_rows["QRC14x7"]
    qrc8 = focus_rows["QRC8x5"]
    rc = focus_rows["RC"]
    ets = focus_rows["ETS"]
    xgb = focus_rows["XGBoost"]
    best_objective = ctx["qrc_best_objective"]
    best_extended = ctx["qrc_best_extended"]

    qrc_compare_table = markdown_table(
        ["Modelo", "MAE", "RMSE", "WAPE", "sMAPE"],
        [
            ["QRC14x7", fmt(qrc14["mae"]), fmt(qrc14["rmse"]), fmt(qrc14["wape"], 4), fmt(qrc14["smape"], 4)],
            ["QRC8x5", fmt(qrc8["mae"]), fmt(qrc8["rmse"]), fmt(qrc8["wape"], 4), fmt(qrc8["smape"], 4)],
        ],
    )

    final_compare_table = markdown_table(
        ["Modelo", "MAE", "RMSE", "WAPE", "sMAPE"],
        [
            ["ETS", fmt(ets["mae"]), fmt(ets["rmse"]), fmt(ets["wape"], 4), fmt(ets["smape"], 4)],
            ["XGBoost", fmt(xgb["mae"]), fmt(xgb["rmse"]), fmt(xgb["wape"], 4), fmt(xgb["smape"], 4)],
            ["RC", fmt(rc["mae"]), fmt(rc["rmse"]), fmt(rc["wape"], 4), fmt(rc["smape"], 4)],
            ["QRC14x7", fmt(qrc14["mae"]), fmt(qrc14["rmse"]), fmt(qrc14["wape"], 4), fmt(qrc14["smape"], 4)],
            ["QRC8x5", fmt(qrc8["mae"]), fmt(qrc8["rmse"]), fmt(qrc8["wape"], 4), fmt(qrc8["smape"], 4)],
        ],
    )

    qrc14_vs_rc_mae = (float(qrc14["mae"]) / float(rc["mae"]) - 1.0) * 100.0
    qrc14_vs_ets_mae = (float(qrc14["mae"]) / float(ets["mae"]) - 1.0) * 100.0

    return dedent(
        rf"""
        # Quantum Reservoir Computing para previsao de demanda: um estudo didatico com o Favorita

        ## Resumo

        Este artigo fecha a serie com um estudo completo e didatico de Quantum Reservoir Computing (QRC) aplicado ao recorte adotado no Favorita desde o primeiro capitulo. O texto unifica tudo o que foi construido anteriormente: problema de negocio, protocolo experimental, benchmark justo, intuicao de reservatorio e ponte conceitual para o quantico. Em seguida, apresenta o pipeline do QRC implementado com Qiskit, compara as configuracoes `14x7` e `8x5`, discute a funcao objetivo usada no tuning e posiciona os resultados do QRC ao lado de `ETS`, `XGBoost` e `RC`. O resultado final e instrutivo: o QRC funciona de ponta a ponta, `14x7` e a melhor configuracao por desempenho puro, `8x5` e o melhor compromisso pela funcao objetivo, mas as tecnicas classicas seguem superiores neste recorte.

        ## 1. O que o leitor vai aprender

        Ao final deste artigo, voce sera capaz de:

        1. descrever o pipeline completo de QRC do projeto;
        2. executar o modelo com Qiskit no recorte adotado no Favorita;
        3. interpretar por que `14x7` e `8x5` coexistem como candidatos fortes;
        4. comparar o QRC com RC e modelos classicos no mesmo protocolo;
        5. concluir o que a serie inteira ensina sobre a rota ate QRC.

        ## 2. O recorte experimental herdado da serie

        O estudo final nao muda o problema para favorecer o QRC. Ele preserva:

        - `store_nbr = 1`
        - `family = BEVERAGES`
        - frequencia diaria
        - ultimos `90` dias como teste

        Isso garante continuidade didatica e comparabilidade cientifica.

        ## 3. Pipeline de QRC usado no projeto

        ### 3.1 Entrada

        O QRC usa um vetor de entrada classico reduzido:

        $$
        u_t =
        \begin{{bmatrix}}
        \widetilde{{y}}_{{t-1}} &
        \widetilde{{p}}_t &
        \sin(2\pi \, \mathrm{{dow}}_t / 7) &
        \cos(2\pi \, \mathrm{{dow}}_t / 7)
        \end{{bmatrix}}^\top.
        $$

        Essa reducao aparece em `_quantum_input_vector()`, que seleciona os quatro primeiros componentes do vetor sequencial classico.

        ### 3.2 Dinamica quantica

        Para cada passo da janela, o circuito aplica rotacoes `RX` e `RY` em todos os qubits e um anel de emaranhamento `CZ` + `RZ`. Se chamarmos o operador de um passo de $U(u_t)$, a representacao da janela fica

        $$
        |\psi_t\rangle = U(u_t) U(u_{{t-1}}) \cdots U(u_{{t-w+1}}) |0 \cdots 0\rangle.
        $$

        ### 3.3 Observaveis

        As features quanticas sao expectativas:

        $$
        z_t^{{(j)}} = \langle \psi_t | O_j | \psi_t \rangle.
        $$

        O projeto usa observaveis `Z`, `X` e `ZZ`, totalizando `3q` componentes para `q` qubits.

        ### 3.4 Readout

        O readout final continua sendo simples:

        $$
        \hat{{y}}_t = W_{{out}} [1; u_t; z_t],
        $$

        com treinamento Ridge:

        $$
        W_{{out}}^* = \arg\min_{{W_{{out}}}} \|Y - \Phi W_{{out}}\|_2^2 + \lambda \|W_{{out}}\|_2^2.
        $$

        Em outras palavras, o QRC do projeto herda a filosofia central de RC: dinamica rica, readout simples.

        ## 4. Implementacao passo-a-passo

        O leitor pode percorrer a implementacao nesta ordem.

        ### 4.1 Passo 1: definir a configuracao

        ```python
        @dataclass(frozen=True)
        class QRCConfig:
            n_qubits: int = 14
            window: int = 7
            input_scale: float = 1.2
            ridge_alpha: float = 1e-1
            seed: int = 7
        ```

        ### 4.2 Passo 2: construir o circuito por passo

        O codigo central esta em `_step_circuit()` e usa `QuantumCircuit` do Qiskit.

        ### 4.3 Passo 3: acumular a janela quantica

        `features_from_window()` compoe sucessivos passos do circuito antes de criar o `Statevector`.

        ### 4.4 Passo 4: medir observaveis

        O metodo `_build_observables()` cria as listas de operadores `Z`, `X` e `ZZ`.

        ### 4.5 Passo 5: ajustar o readout e prever

        `fit_qrc_readout()` treina o Ridge e `forecast_qrc()` faz previsao recursiva no bloco de teste.

        Para executar:

        ```bash
        python code/qrc/run.py
        pytest code/qrc/test_model.py
        pytest code/qrc/test_objective.py
        ```

        ## 5. Configuracao experimental

        O tuning anterior deixou duas configuracoes principais:

        - melhor configuracao por rank medio multi-metrica: `{best_extended["best"]["n_qubits"]}x{best_extended["best"]["window"]}`
        - melhor configuracao pela funcao objetivo escalar: `{best_objective["best"]["n_qubits"]}x{best_objective["best"]["window"]}`

        O artigo final preserva as duas porque elas respondem a perguntas diferentes:

        - "qual performa melhor nas metricas?" -> `14x7`
        - "qual equilibra melhor desempenho e complexidade?" -> `8x5`

        ## 6. Resultados do QRC

        A comparacao direta entre as duas configuracoes ficou assim:

        {qrc_compare_table}

        {figure_block(results_name, "qrc_14x7_vs_8x5.png", "Comparacao direta entre as configuracoes QRC14x7 e QRC8x5.")}

        {figure_block(results_name, "qrc_focus_mae_bars.png", "Comparacao em barras para o MAE entre modelos de referencia e QRC.")}

        A leitura dos dois pontos e clara:

        - `14x7` foi melhor que `8x5` nas quatro metricas no run direto;
        - `8x5` permaneceu relevante porque sua funcao objetivo penalizada era melhor;
        - o trade-off entre desempenho e complexidade foi real, nao artificial.

        ## 7. Comparacao com RC e tecnicas classicas

        O QRC precisa ser lido ao lado do benchmark herdado, nao isoladamente.

        {final_compare_table}

        O ponto central do estudo e este:

        - `QRC14x7` ficou cerca de {qrc14_vs_rc_mae:.1f}% acima do `RC` em `MAE`;
        - `QRC14x7` ficou cerca de {qrc14_vs_ets_mae:.1f}% acima do `ETS` em `MAE`;
        - ainda assim, o pipeline quantico funcionou de ponta a ponta no mesmo recorte de negocio.

        ## 8. O que os resultados mostram e o que eles nao mostram

        ### 8.1 O que mostram

        - QRC pode ser implementado de modo didatico e reprodutivel com Qiskit;
        - tuning de `qubits` e `window` importa muito;
        - o melhor QRC do projeto foi `14x7`;
        - comparacoes honestas sao possiveis no mesmo recorte adotado no Favorita.

        ### 8.2 O que nao mostram

        - que QRC seja superior a tecnicas classicas neste problema;
        - que aumentar qubits sempre melhora desempenho;
        - que o estudo atual esgote o espaco de arquiteturas quanticas possiveis.

        ## 9. A contribuicao didatica do estudo final

        O estudo final nao vale apenas pela tabela de metricas. Ele vale porque fecha uma trilha de ensino completa:

        1. do problema de negocio;
        2. aos baselines;
        3. ao RC classico;
        4. ao tuning;
        5. ao benchmark justo;
        6. a ponte quantica;
        7. ao QRC implementado e comparado.

        Essa sequencia e o que transforma o conjunto dos sete artigos em um material "101" real para QRC.

        ## 10. O que o leitor aprendeu do artigo 1 ao 7

        Ao final da serie, o leitor passou a saber:

        - formular um problema real de previsao de demanda;
        - construir um protocolo temporal correto;
        - comparar baselines, IA classica, RC e QRC;
        - ler e modificar as implementacoes do projeto;
        - interpretar resultados negativos ou medianos sem perder valor cientifico;
        - entender QRC como extensao do paradigma de reservatorio, e nao como curiosidade isolada.

        ## 11. Conclusao

        O QRC do projeto funciona, ensina, compara e fecha a serie de forma honesta. O melhor resultado puro ficou em `14x7`; o melhor compromisso com penalizacao de complexidade ficou em `8x5`. Nenhum dos dois venceu os melhores modelos classicos no recorte adotado no Favorita, mas ambos cumprem o papel mais importante desta obra: ensinar, de forma continua e reproduzivel, como sair do zero e chegar a um estudo completo de Quantum Reservoir Computing aplicado a um problema real.

        ## Entregaveis associados no repositorio

        - implementacao do QRC: `code/qrc/`
        - tuning e funcao objetivo: `code/qrc/objective.py`, `code/qrc/OBJECTIVE.md`
        - benchmark consolidado: `code/RESULTS.md`
        - artefatos deste artigo: `{results_name}/`

        ## Referencias

        - Fujii, K.; Nakajima, K. Harnessing disordered-ensemble quantum dynamics for machine learning.
        - Ghosh, S. et al. Quantum reservoir processing.
        - Qiskit documentation.
        - Jaeger, H. The "echo state" approach to analysing and training recurrent neural networks.
        - Monzani, F.; Ricci, E.; Nigro, L.; Prati, E. QRC-Lab: An Educational Toolbox for Quantum Reservoir Computing. arXiv:2602.03522.
        """
    ).strip() + "\n"


def split_markdown_document(text: str) -> tuple[str, str, str]:
    lines = text.strip().splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError("markdown document must start with a level-1 title")
    title = lines[0][2:].strip()

    resumo_idx = None
    next_section_idx = None
    for idx, line in enumerate(lines):
        if line.strip() == "## Resumo":
            resumo_idx = idx
            break
    if resumo_idx is None:
        raise ValueError("markdown document is missing '## Resumo'")

    for idx in range(resumo_idx + 1, len(lines)):
        if lines[idx].startswith("## "):
            next_section_idx = idx
            break
    if next_section_idx is None:
        raise ValueError("markdown document is missing body sections after resumo")

    abstract_md = "\n".join(lines[resumo_idx + 1 : next_section_idx]).strip()
    body_md = "\n".join(lines[next_section_idx:]).strip()
    return title, abstract_md, body_md


def pandoc_to_latex(markdown_text: str) -> str:
    result = subprocess.run(
        [
            "pandoc",
            "--from",
            "gfm+tex_math_dollars+pipe_tables+raw_attribute",
            "--to",
            "latex",
            "--wrap=preserve",
            "--no-highlight",
        ],
        input=markdown_text,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


HEADING_PREFIX_PATTERN = r"\d+(?:\.\d+)*\.?\s+"
AUTHOR_NAME = "Anderson Fernandes Pereira dos Santos"
AUTHOR_FOOTER = "SANTOS, Anderson F. P. dos"
AUTHOR_ADDRESS_LATEX = dedent(
    r"""
    Instituto Militar de Engenharia (IME), Rio de Janeiro, Brazil \\
    Venturus Innovation Center, Campinas, Brazil \\
    \texttt{anderson@ime.eb.br} | \texttt{anderson.santos@venturus.org.br}
    """
).strip()
DISPLAY_TITLES = {
    "02": "Fundamentos de Reservoir Computing",
    "03": "Primeiro pipeline reproduzível",
    "04": "Memória e não linearidade em RC",
    "05": "Avaliação e boas práticas",
    "06": "RC físico e ponte para QRC",
    "07": "Quantum Reservoir Computing para previsão de demanda",
}
STANDARD_REFERENCE_BLOCK_03_TO_07 = dedent(
    r"""
    \section{Referências}\label{referencias}

    \begin{thebibliography}{9}

    \bibitem{jaeger2001}
    JAEGER, H. \textbf{The ``echo state'' approach to analysing and training recurrent neural networks}. Bonn: German National Research Center for Information Technology (GMD), 2001.

    \bibitem{lukosevicius2009}
    LUKOSEVICIUS, M.; JAEGER, H. \textbf{Reservoir computing approaches to recurrent neural network training}. \emph{Computer Science Review}, v. 3, n. 3, p. 127--149, 2009.

    \bibitem{lukosevicius2012}
    LUKOSEVICIUS, M. \textbf{A practical guide to applying echo state networks}. In: MONTAVON, G.; ORR, G. B.; MÜLLER, K.-R. (org.). \emph{Neural Networks: Tricks of the Trade}. 2. ed. Berlin: Springer, 2012. p. 659--686.

    \bibitem{fujii2017}
    FUJII, K.; NAKAJIMA, K. \textbf{Harnessing disordered-ensemble quantum dynamics for machine learning}. \emph{Physical Review Applied}, v. 8, n. 2, 024030, 2017.

    \end{thebibliography}
    """
).strip()


def strip_numeric_heading_prefix(title: str) -> str:
    title = re.sub(rf"^{HEADING_PREFIX_PATTERN}", "", title)
    title = re.sub(rf"(\\texorpdfstring\{{){HEADING_PREFIX_PATTERN}", r"\1", title)
    title = re.sub(rf"(\}}\{{){HEADING_PREFIX_PATTERN}", r"\1", title)
    return title


def normalize_latex_heading_line(line: str, command: str, replacement: str) -> str | None:
    prefix = f"\\{command}{{"
    if not (line.startswith(prefix) and "}\\label{" in line):
        return None
    title, _, label_tail = line[len(prefix) :].partition("}\\label{")
    title = strip_numeric_heading_prefix(title)
    return f"\\{replacement}{{{title}}}\\label{{{label_tail}"


def promote_latex_heading_hierarchy(tex: str) -> str:
    updated_lines: list[str] = []
    for line in tex.splitlines():
        normalized = normalize_latex_heading_line(line, "section", "section")
        if normalized is not None:
            updated_lines.append(normalized)
            continue

        normalized = normalize_latex_heading_line(line, "subsection", "section")
        if normalized is not None:
            updated_lines.append(normalized)
            continue

        normalized = normalize_latex_heading_line(line, "subsubsection", "subsection")
        if normalized is not None:
            updated_lines.append(normalized)
            continue

        updated_lines.append(line)

    return "\n".join(updated_lines)


PANDOC_IMAGE_PATTERN = re.compile(
    r"\\pandocbounded\{\\includegraphics\[(?P<options>[^\]]*?)alt=\{(?P<caption>.*?)\}[^\]]*?\]\{(?P<path>.*?)\}\}",
    flags=re.DOTALL,
)


def convert_pandoc_images_to_figures(tex: str) -> str:
    def replacer(match: re.Match[str]) -> str:
        caption = " ".join(match.group("caption").split())
        path = match.group("path").strip()
        return dedent(
            rf"""
            \begin{{figure}}[htbp]
            \centering
            \includegraphics[width=\linewidth,keepaspectratio]{{{path}}}
            \caption{{{caption}}}
            \end{{figure}}
            """
        ).strip()

    return PANDOC_IMAGE_PATTERN.sub(replacer, tex)


def replace_references_with_standard_block(tex: str) -> str:
    pattern = re.compile(
        r"\\section\{Refer[eê]ncias\}\\label\{referencias\}\s*.*\Z",
        flags=re.DOTALL,
    )
    if not pattern.search(tex):
        return tex
    return pattern.sub(lambda _match: STANDARD_REFERENCE_BLOCK_03_TO_07, tex)


def normalize_article_body_for_series_template(tex: str) -> str:
    tex = promote_latex_heading_hierarchy(tex)
    tex = convert_pandoc_images_to_figures(tex)
    tex = tex.replace(
        r"\section{Entregaveis associados no repositorio}\label{entregaveis-associados-no-repositorio}",
        r"\section*{Entregaveis associados no repositorio}\label{entregaveis-associados-no-repositorio}",
    )
    tex = replace_references_with_standard_block(tex)
    return tex


def build_latex_document(
    title: str,
    abstract_md: str,
    body_md: str,
    article_key: str | None = None,
) -> str:
    abstract_tex = pandoc_to_latex(abstract_md)
    body_tex = pandoc_to_latex(body_md)
    if article_key in {"02", "03", "04", "05", "06", "07"}:
        body_tex = normalize_article_body_for_series_template(body_tex)
        display_title = DISPLAY_TITLES.get(article_key, title)
        footer_title = display_title
        return dedent(
            rf"""
            \documentclass[12pt]{{article}}
            \usepackage{{sbc-template}}
            \makeatletter
            \renewcommand{{\inst}}[1]{{}}
            \makeatother
            \usepackage{{graphicx,url}}
            \usepackage[utf8]{{inputenc}}
            \usepackage[T1]{{fontenc}}
            \usepackage[brazil]{{babel}}
            \usepackage{{longtable,booktabs,array,tabularx}}
            \usepackage{{amsmath,amssymb}}
            \usepackage{{fvextra}}
            \newcolumntype{{Y}}{{>{{\raggedright\arraybackslash}}X}}
            \newcolumntype{{C}}{{>{{\centering\arraybackslash}}X}}
            \setlength{{\LTleft}}{{0pt}}
            \setlength{{\LTright}}{{0pt}}
            \RecustomVerbatimEnvironment{{verbatim}}{{Verbatim}}{{%
              breaklines=true,
              breakanywhere=true,
              breaksymbolleft={{}},
              fontsize=\small
            }}
            \providecommand{{\tightlist}}{{%%
              \setlength{{\itemsep}}{{0pt}}\setlength{{\parskip}}{{0pt}}}}
            \providecommand{{\pandocbounded}}[1]{{#1}}
            \usepackage{{fancyhdr}}
            \pagestyle{{fancy}}
            \fancyhf{{}}
            \fancyfoot[R]{{\thepage}}
            \fancyfoot[L]{{{AUTHOR_FOOTER} — {footer_title}}}
            \renewcommand{{\headrulewidth}}{{0pt}}
            \renewcommand{{\footrulewidth}}{{0.4pt}}
            \sloppy
            \title{{{display_title}}}
            \author{{{AUTHOR_NAME}}}
            \address{{{AUTHOR_ADDRESS_LATEX}}}
            \begin{{document}}

            \maketitle

            \begin{{resumo}}
            {abstract_tex}
            \end{{resumo}}

            {body_tex}

            \end{{document}}
            """
        ).strip() + "\n"
    return dedent(
        rf"""
        \documentclass[12pt]{{article}}
        \makeatletter
        \def\input@path{{{{../../}}}}
        \makeatother
        \usepackage{{sbc-template}}
        \makeatletter
        \renewcommand{{\inst}}[1]{{}}
        \makeatother
        \usepackage{{graphicx,url}}
        \usepackage[utf8]{{inputenc}}
        \usepackage[T1]{{fontenc}}
        \usepackage[brazil]{{babel}}
        \usepackage{{longtable,booktabs,array,tabularx}}
        \usepackage{{amsmath,amssymb}}
        \usepackage{{fvextra}}
        \newcolumntype{{Y}}{{>{{\raggedright\arraybackslash}}X}}
        \newcolumntype{{C}}{{>{{\centering\arraybackslash}}X}}
        \setlength{{\LTleft}}{{0pt}}
        \setlength{{\LTright}}{{0pt}}
        \RecustomVerbatimEnvironment{{verbatim}}{{Verbatim}}{{%
          breaklines=true,
          breakanywhere=true,
          breaksymbolleft={{}},
          fontsize=\small
        }}
        \providecommand{{\tightlist}}{{%%
          \setlength{{\itemsep}}{{0pt}}\setlength{{\parskip}}{{0pt}}}}
        \sloppy
        \title{{{title}}}
        \author{{}}
        \address{{}}
        \begin{{document}}

        \maketitle

        \begin{{resumo}}
        {abstract_tex}
        \end{{resumo}}

        {body_tex}

        \end{{document}}
        """
    ).strip() + "\n"


def write_markdown_files(context: dict[str, dict]) -> None:
    builders = {
        "01": build_article_01,
        "02": build_article_02,
        "03": build_article_03,
        "04": build_article_04,
        "05": build_article_05,
        "06": build_article_06,
        "07": build_article_07,
    }
    for key, builder in builders.items():
        article_dir = context[key]["article_dir"]
        manuscript_path = article_dir / "MANUSCRIPT.md"
        manuscript_path.write_text(normalize_markdown(builder(context)), encoding="utf-8")


def build_latex_bundle(context: dict[str, dict]) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for key, article in context.items():
        if key not in ARTICLE_DIRS:
            continue
        article_dir = article["article_dir"]
        markdown_path = article_dir / "MANUSCRIPT.md"
        latex_dir = article_dir / f"latex_{timestamp}"
        latex_dir.mkdir(parents=True, exist_ok=False)

        results_dir = article["results_dir"]
        shutil.copytree(results_dir, latex_dir / results_dir.name)
        shutil.copy2(SBC_TEMPLATE, latex_dir / SBC_TEMPLATE.name)
        shutil.copy2(SBC_BST, latex_dir / SBC_BST.name)

        title, abstract_md, body_md = split_markdown_document(markdown_path.read_text(encoding="utf-8"))
        tex_content = build_latex_document(title, abstract_md, body_md, article_key=key)
        tex_path = latex_dir / "MANUSCRIPT.tex"
        tex_path.write_text(tex_content, encoding="utf-8")

        for _ in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "MANUSCRIPT.tex"],
                cwd=latex_dir,
                capture_output=True,
            )
            if result.returncode not in (0, 1):
                raise RuntimeError(
                    f"pdflatex failed for {tex_path} with exit code {result.returncode}\n"
                    f"{result.stdout.decode('utf-8', errors='ignore')}\n"
                    f"{result.stderr.decode('utf-8', errors='ignore')}"
                )

        pdf_path = latex_dir / "MANUSCRIPT.pdf"
        if not pdf_path.exists():
            raise FileNotFoundError(f"expected PDF was not created for {tex_path}")

    return timestamp


def main() -> None:
    context = load_context()
    write_markdown_files(context)
    timestamp = build_latex_bundle(context)
    print(json.dumps({"status": "ok", "latex_timestamp": timestamp}, indent=2))


if __name__ == "__main__":
    main()
