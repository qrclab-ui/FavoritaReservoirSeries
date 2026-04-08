# Artigo 4

## Titulo sugerido

Por que Reservoir Computing funciona: memoria, nao linearidade e capacidade de representacao

## Pergunta central

Quais propriedades do reservatorio ajudam de fato na previsao de demanda?

## Contribuicao do artigo

Explicar o ganho de RC nao apenas em termos de desempenho, mas em termos de propriedades mecanicas do modelo: memoria temporal, mistura nao linear e separabilidade.

## O que o leitor aprende

- o que significa memoria no contexto de forecasting;
- por que nao linearidade importa em promocoes e eventos;
- como hiperparametros alteram comportamento do reservatorio;
- como interpretar resultados alem de uma unica metrica.

## Estrutura sugerida

1. Revisao do experimento anterior
   Relembrar o pipeline inicial e suas limitacoes.
2. O conceito de memoria
   Relacionar janelas temporais, lags e dependencia no passado.
3. O conceito de nao linearidade
   Explicar resposta a promocoes, feriados e mudancas abruptas.
4. Experimentos de ablacao
   Variar tamanho do reservatorio, profundidade, leak rate ou outro hiperparametro chave.
5. Analise qualitativa
   Mostrar onde o modelo melhora e onde falha.
6. Interpretacao didatica
   Conectar resultados a capacidade de representacao.
7. Transicao para avaliacao rigorosa
   Preparar o terreno para comparacoes mais justas.

## Entregaveis do artigo

- estudo de sensibilidade dos hiperparametros;
- figuras de memoria e resposta nao linear;
- leitura intuitiva do funcionamento do RC;
- hipoteses para comparar RC com outros modelos.
