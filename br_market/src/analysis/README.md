# Análise e Visualização de Sentimento e Retorno de Ações Brasileiras

## Visão Geral
Este script realiza uma análise detalhada e cria visualizações dos dados de sentimento e retorno das ações brasileiras. Ele processa os dados coletados, calcula estatísticas relevantes e gera uma série de gráficos informativos.

## Funcionalidades

1. **Carregamento e Pré-processamento de Dados**
   - Lê o arquivo CSV com dados de sentimento e histórico de preços.
   - Realiza conversões seguras de tipos de dados.

2. **Análise Estatística**
   - Calcula médias de sentimento para empresas principais.
   - Computa estatísticas adicionais como range de datas, retorno médio de 7 dias e distribuição de sentimentos.

3. **Visualizações**
   - Gráfico de barras empilhadas para scores de sentimento.
   - Heatmap de scores de sentimento.
   - Gráficos de dispersão para sentimento positivo/negativo vs. retorno de 7 dias.
   - Boxplot da distribuição de scores de sentimento.
   - Gráficos de radar para top 5 empresas por sentimento positivo e negativo.

## Uso

1. Certifique-se de que o arquivo de dados `brazilian_stocks_with_sentiment_and_historical_data_[DATA].csv` está na pasta correta.
2. Execute o script:
   ```
   python analysis_script.py
   ```
3. As visualizações serão salvas como arquivos PNG na mesma pasta do script.

## Dependências

- pandas
- matplotlib
- seaborn
- numpy
- scipy

## Estrutura de Dados

O script espera um DataFrame com as seguintes colunas:
- Ticker
- Date
- Positive_Score
- Negative_Score
- Neutral_Score
- Overall_Sentiment
- 7d_Return

## Resultados Principais

- Scores médios de sentimento para as principais empresas brasileiras.
- Correlação entre sentimento positivo/negativo e retornos de 7 dias.
- Visualização das empresas com maior sentimento positivo e negativo.
- Distribuição geral dos scores de sentimento entre as empresas.

## Notas

- O script foca em um conjunto predefinido de empresas consideradas "principais", pode escolher a empresa que quiser, desde que esteja presente no arquivo csv.
- Algumas visualizações são personalizadas com nomes completos das empresas para melhor legibilidade.
- Os gráficos são salvos com alta resolução (300 dpi) para uso em apresentações ou relatórios.