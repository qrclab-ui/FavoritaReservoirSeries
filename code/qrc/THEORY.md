# Fundamento teorico

Quantum Reservoir Computing aplica a ideia de Reservoir Computing a sistemas quanticos.

## Ideia central

Em vez de um reservatorio recorrente classico, usamos um sistema quantico parametrizado pelas entradas e observamos certas medidas do estado resultante.

Em alto nivel, o fluxo e:

1. codificar a entrada em um circuito quantico;
2. aplicar uma dinamica quantica fixa;
3. medir observaveis;
4. treinar apenas um readout classico.

## Variante usada aqui

Nesta implementacao usamos uma forma didatica de QRC com reuploading:

- uma janela curta de entradas e codificada em camadas sucessivas do circuito;
- o circuito tem pesos quanticos fixos;
- o estado final e medido por observaveis como `Z`, `X` e correlacoes `ZZ`;
- um readout linear aprende a prever a demanda.

## Por que essa escolha

Ela e util para ensino porque:

- usa Qiskit diretamente;
- evita um custo computacional excessivo;
- preserva a intuicao de "dinamica rica + readout simples";
- aproxima o caso de hardware em que reuploading e uma estrategia natural.

## Papel didatico nesta serie

Este codigo fecha a ponte entre RC e QRC:

- no RC, o estado vem de um reservatorio recorrente classico;
- no QRC, o estado observado emerge da evolucao de um circuito quantico fixo.
