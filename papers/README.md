# Papers

Serie didatica planejada como uma obra "QRC 101", partindo do zero e chegando a um estudo aplicado de Quantum Reservoir Computing para previsao de demanda e otimizacao de estoque com o dataset Favorita.

## Objetivo da obra

Ao final dos 7 artigos, o leitor deve ser capaz de:

1. entender o problema de negocio de previsao de demanda;
2. compreender os fundamentos de Reservoir Computing;
3. implementar e avaliar modelos classicos e RC em um protocolo temporal justo;
4. entender por que QRC e uma extensao natural de RC;
5. reproduzir um estudo inicial de QRC em um subconjunto realista do Favorita.

## Fio condutor didatico

Toda a serie usa o mesmo caso central:

- previsao de demanda no Favorita;
- foco em um recorte reproduzivel;
- comparacao progressiva entre baselines, IA classica, RC e QRC;
- mesma logica de negocio do inicio ao fim.

## Principios editoriais

- Cada artigo precisa ensinar uma ideia principal.
- Cada artigo precisa entregar uma contribuicao propria.
- Cada artigo precisa deixar um resultado concreto ou reproduzivel.
- O conjunto dos 7 precisa funcionar como uma introducao progressiva e coerente.

## Ordem e papel de cada artigo

1. `01_motivacao_e_negocio`
   Papel: mostrar por que o problema importa.
2. `02_fundamentos_de_rc`
   Papel: apresentar o paradigma de Reservoir Computing.
3. `03_primeiro_modelo_previsao`
   Papel: construir o primeiro pipeline reproduzivel.
4. `04_memoria_nao_linearidade`
   Papel: explicar por que RC funciona.
5. `05_avaliacao_e_boas_praticas`
   Papel: ensinar a comparar modelos com rigor.
6. `06_rc_fisico_e_ponte_para_qrc`
   Papel: preparar a transicao conceitual para QRC.
7. `07_qrc_para_previsao_de_demanda`
   Papel: fechar a serie com um estudo aplicado de QRC.

## Manuscritos entregues

Cada pasta de artigo agora contem um manuscrito completo em `MANUSCRIPT.md`:

1. `01_motivacao_e_negocio/MANUSCRIPT.md`
2. `02_fundamentos_de_rc/MANUSCRIPT.md`
3. `03_primeiro_modelo_previsao/MANUSCRIPT.md`
4. `04_memoria_nao_linearidade/MANUSCRIPT.md`
5. `05_avaliacao_e_boas_praticas/MANUSCRIPT.md`
6. `06_rc_fisico_e_ponte_para_qrc/MANUSCRIPT.md`
7. `07_qrc_para_previsao_de_demanda/MANUSCRIPT.md`

## Resultado esperado da serie

Se os 7 textos forem escritos seguindo esta estrutura, o conjunto deixa de ser apenas uma colecao de artigos e passa a funcionar como um curso introdutorio em formato de paper series:

- Artigos 1 e 2: contexto e fundamentos.
- Artigos 3, 4 e 5: pratica, explicacao e avaliacao.
- Artigos 6 e 7: ponte conceitual e aplicacao em QRC.
