import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# Nome do ficheiro de base de dados
DB_FILE = "inventario.csv"

def carregar_dados():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Validade'] = pd.to_datetime(df['Validade']).dt.date
        return df
    return pd.DataFrame(columns=["Produto", "Quantidade", "Categoria", "Validade"])

def guardar_dados(df):
    df.to_csv(DB_FILE, index=False)

# Configuração da página da aplicação
st.set_page_config(page_title="EcoTrack - Gestor de Alimentos", page_icon="🌱", layout="wide")

# Inicializar estado da sessão para armazenar os alimentos
if 'inventario' not in st.session_state:
    st.session_state.inventario = carregar_dados()

st.title("🌱 EcoTrack - Reduza o Desperdício")
st.subheader("O seu gestor de validade inteligente")

# Categorias predefinidas
CATEGORIAS = ["Frigorífico", "Despensa", "Congelador", "Frutaria", "Outros"]

# Barra lateral para entrada de novos dados
with st.sidebar:
    st.header("Adicionar Alimento")
    with st.form("novo_alimento", clear_on_submit=True):
        nome = st.text_input("Produto")
        col_q, col_c = st.columns(2)
        quantidade = col_q.number_input("Qtd", min_value=1, value=1)
        categoria = col_c.selectbox("Categoria", CATEGORIAS)
        data_validade = st.date_input("Data de Validade", min_value=date.today())
        submetido = st.form_submit_button("Registar")
        
        if submetido:
            if nome:
                novo_item = pd.DataFrame({
                    "Produto": [nome], 
                    "Quantidade": [quantidade],
                    "Categoria": [categoria],
                    "Validade": [data_validade]
                })
                st.session_state.inventario = pd.concat([st.session_state.inventario, novo_item], ignore_index=True)
                guardar_dados(st.session_state.inventario)
                st.success(f"{nome} adicionado!")
                st.rerun()
            else:
                st.error("Por favor, insira o nome do produto.")

# Lógica de processamento e visualização do inventário
df = st.session_state.inventario.copy()

if not df.empty:
    # Garantir que a validade está no formato correto
    df['Validade'] = pd.to_datetime(df['Validade']).dt.date
    hoje = date.today()
    df['Dias para Vencer'] = (df['Validade'] - hoje).apply(lambda x: x.days)
    
    # Filtros
    st.write("### Filtros")
    col_f1, col_f2 = st.columns(2)
    filtro_cat = col_f1.multiselect("Filtrar por Categoria", CATEGORIAS)
    busca = col_f2.text_input("Procurar Produto")

    if filtro_cat:
        df = df[df['Categoria'].isin(filtro_cat)]
    if busca:
        df = df[df['Produto'].str.contains(busca, case=False)]

    # Cálculo e exibição de métricas rápidas
    col1, col2, col3 = st.columns(3)
    vencidos = len(df[df['Dias para Vencer'] < 0])
    alerta = len(df[(df['Dias para Vencer'] >= 0) & (df['Dias para Vencer'] <= 3)])
    
    col1.metric("Total de Itens", len(df))
    col2.metric("Em Alerta (≤ 3 dias)", alerta)
    col3.metric("Vencidos", vencidos)

    st.write("### O seu Inventário")
    
    def colorir_validade(row):
        if row['Dias para Vencer'] < 0:
            return ['background-color: #ff4b4b'] * len(row)
        elif row['Dias para Vencer'] <= 3:
            return ['background-color: #ffa500'] * len(row)
        return [''] * len(row)

    # Ordenar por data de validade
    df_visual = df.sort_values(by="Validade")
    
    # Exibir a tabela formatada
    st.dataframe(df_visual.style.apply(colorir_validade, axis=1), use_container_width=True)

    # Gestão de Itens (Remover)
    with st.expander("🗑️ Gerir / Remover Itens"):
        item_para_remover = st.selectbox("Escolha um item para remover", df.index, format_func=lambda x: f"{df.loc[x, 'Produto']} ({df.loc[x, 'Categoria']})")
        if st.button("Remover Item Selecionado"):
            st.session_state.inventario = st.session_state.inventario.drop(item_para_remover).reset_index(drop=True)
            guardar_dados(st.session_state.inventario)
            st.success("Item removido!")
            st.rerun()

    # Botão para limpar todos os dados
    if st.button("Limpar Tudo (CUIDADO)"):
        st.session_state.inventario = pd.DataFrame(columns=["Produto", "Quantidade", "Categoria", "Validade"])
        guardar_dados(st.session_state.inventario)
        st.rerun()
else:
    st.info("O seu inventário está vazio. Adicione produtos na barra lateral!")

# Secção informativa para o utilizador
with st.expander("💡 Dicas para reduzir o desperdício"):
    st.write("""
    1. **Planeie as refeições:** Veja o que tem no EcoTrack antes de ir às compras.
    2. **Primeiro a entrar, primeiro a sair:** Coloque os itens mais antigos à frente no frigorífico.
    3. **Congele:** Muitos alimentos podem ser congelados se vir que não os vai consumir a tempo.
    4. **Organize por categorias:** Use as categorias para saber exatamente onde procurar os seus alimentos.
    """)