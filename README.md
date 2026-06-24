# 🌱 AlgorithmicFresh - Gestor de Desperdício Alimentar

O **AlgorithmicFresh** é uma aplicação inteligente desenvolvida com Streamlit para ajudar os utilizadores a gerir a validade dos seus alimentos, reduzindo o desperdício e promovendo o consumo consciente.

## 🚀 Funcionalidades

- **Gestão de Inventário Completa**: Adicione produtos com nome, quantidade, categoria e data de validade.
- **Persistência de Dados**: Os seus alimentos são guardados num ficheiro local (`inventario.csv`), para que não perca nada ao fechar a aplicação.
- **Categorização Inteligente**: Organize os seus alimentos por local de armazenamento (Frigorífico, Despensa, etc.).
- **Sistema de Filtros e Busca**: Encontre rapidamente o que precisa através de filtros por categoria ou busca por nome.
- **Métricas em Tempo Real**: Visualize rapidamente o total de itens, quantos estão próximos da validade (3 dias) e quantos já expiraram.
- **Gestão de Itens**: Remova itens individualmente ou limpe todo o inventário quando necessário.
- **Botão Consumir**: Remova rapidamente um item do inventário ao consumi-lo, mantendo o ficheiro atualizado.
- **Botão Congelar**: Prolongue a validade de um produto em 90 dias e mova-o automaticamente para a categoria "Congelador".
- **Visualização Colorida**:
  - 🟠 **Laranja**: Alimentos que vencem em 3 dias ou menos.
  - 🔴 **Vermelho**: Alimentos já fora do prazo de validade.
- **Dicas de Sustentabilidade**: Dicas práticas integradas para ajudar a reduzir o desperdício no dia a dia.

## 🛠️ Tecnologias Utilizadas

- **Python**
- **Streamlit**: Para a interface web interativa.
- **Pandas**: Para manipulação e análise de dados.

## 📦 Como Instalar e Correr

1. Certifique-se de que tem o Python instalado.
2. Instale as dependências necessárias:
   ```bash
   pip install streamlit pandas
   ```
3. Execute a aplicação:
   ```bash
   streamlit run main.py
   ```

## 📂 Estrutura do Projeto

- `main.py`: O ficheiro principal que contém toda a lógica da aplicação e interface.
- `README.md`: Documentação do projeto.
