import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# Nome do ficheiro de base de dados
DB_FILE = "inventario.csv"

def carregar_dados():
    """
    Carrega os dados do inventário a partir do ficheiro CSV.
    
    Returns:
        pd.DataFrame: DataFrame contendo o inventário. Se o ficheiro não existir,
                     retorna um DataFrame vazio com as colunas predefinidas.
    """
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # Converter a coluna Validade para o formato de data do Python
        df['Validade'] = pd.to_datetime(df['Validade']).dt.date
        return df
    return pd.DataFrame(columns=["Produto", "Quantidade", "Categoria", "Validade"])

def guardar_dados(df):
    """
    Guarda o DataFrame do inventário no ficheiro CSV.
    
    Args:
        df (pd.DataFrame): O DataFrame a ser persistido.
    """
    df.to_csv(DB_FILE, index=False)

# Configuração da página da aplicação
st.set_page_config(page_title="AlgorithmicFresh - Gestor de Alimentos", page_icon="🌱", layout="wide")

# Título principal da aplicação
st.title("🌱 AlgorithmicFresh - Reduza o Desperdício")
st.subheader("O seu gestor de validade inteligente")

# Inicializar estado da sessão para armazenar os alimentos
# Isto garante que os dados persistem enquanto a aplicação está a correr
if 'inventario' not in st.session_state:
    st.session_state.inventario = carregar_dados()

# Categorias predefinidas para organização dos alimentos
CATEGORIAS = ["Frigorífico", "Despensa", "Congelador", "Frutaria", "Outros"]

# Barra lateral para entrada de novos dados
with st.sidebar:
    st.header("Adicionar Alimento")
    with st.form("novo_alimento", clear_on_submit=True):
        nome = st.text_input("Produto", help="Ex: Leite, Maçãs, Frango")
        col_q, col_c = st.columns(2)
        quantidade = col_q.number_input("Qtd", min_value=1, value=1)
        categoria = col_c.selectbox("Categoria", CATEGORIAS)
        data_validade = st.date_input("Data de Validade", min_value=date.today())
        submetido = st.form_submit_button("Registar")
        
        if submetido:
            if nome:
                # Criar um novo DataFrame para o item e concatenar com o inventário existente
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

# Criar uma cópia do inventário para processamento e filtragem
df = st.session_state.inventario.copy()

if not df.empty:
    # Garantir que a validade está no formato correto e calcular dias restantes
    df['Validade'] = pd.to_datetime(df['Validade']).dt.date
    hoje = date.today()
    df['Dias para Vencer'] = (df['Validade'] - hoje).apply(lambda x: x.days)
    
    # Secção de Filtros
    st.write("### Filtros")
    col_f1, col_f2 = st.columns(2)
    filtro_cat = col_f1.multiselect("Filtrar por Categoria", CATEGORIAS)
    busca = col_f2.text_input("Procurar Produto")

    # Aplicar filtros ao DataFrame se selecionados
    if filtro_cat:
        df = df[df['Categoria'].isin(filtro_cat)]
    if busca:
        df = df[df['Produto'].str.contains(busca, case=False)]

    # Cálculo e exibição de métricas rápidas (KPIs)
    col1, col2, col3 = st.columns(3)
    vencidos = len(df[df['Dias para Vencer'] < 0])
    alerta = len(df[(df['Dias para Vencer'] >= 0) & (df['Dias para Vencer'] <= 3)])
    
    col1.metric("Total de Itens", len(df))
    col2.metric("Em Alerta (≤ 3 dias)", alerta)
    col3.metric("Vencidos", vencidos)

    st.write("### O seu Inventário")
    
    # Ordenar por data de validade para priorizar o que vence primeiro
    df_visual = df.sort_values(by="Validade")
    
    # Exibir o cabeçalho da tabela personalizada (Layout em colunas)
    cols = st.columns([2, 1, 1, 1, 1, 1])
    cols[0].write("**Produto**")
    cols[1].write("**Qtd**")
    cols[2].write("**Categoria**")
    cols[3].write("**Validade**")
    cols[4].write("**Ações**")

    # Iterar sobre os itens para exibir as linhas da tabela
    for idx, row in df_visual.iterrows():
        # Determinar emoji de alerta baseado na proximidade da validade
        cor = ""
        if row['Dias para Vencer'] < 0:
            cor = "🔴" # Vencido
        elif row['Dias para Vencer'] <= 3:
            cor = "🟠" # Próximo do vencimento
        
        c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 1, 1, 1])
        c1.write(f"{cor} {row['Produto']}")
        c2.write(row['Quantidade'])
        c3.write(row['Categoria'])
        c4.write(row['Validade'].strftime('%d/%m/%Y'))
        
        # Botão Consumir (abre um popover para definir quantidade)
        with c5.popover("Consumir"):
            qtd_a_consumir = st.number_input("Quantidade", min_value=1, max_value=int(row['Quantidade']), value=1, key=f"q_cons_{idx}")
            if st.button("Confirmar", key=f"btn_cons_{idx}"):
                if qtd_a_consumir >= row['Quantidade']:
                    # Remover o item se a quantidade total for consumida
                    st.session_state.inventario = st.session_state.inventario.drop(idx).reset_index(drop=True)
                    msg = f"{row['Produto']} totalmente consumido!"
                else:
                    # Subtrair a quantidade consumida
                    st.session_state.inventario.at[idx, 'Quantidade'] -= qtd_a_consumir
                    msg = f"Consumidas {qtd_a_consumir} unidades de {row['Produto']}!"
                
                guardar_dados(st.session_state.inventario)
                st.success(msg)
                st.rerun()
            
        # Botão Congelar (só aparece se o item não estiver no congelador)
        if row['Categoria'] != "Congelador":
            if c6.button("Congelar", key=f"cong_{idx}"):
                # Estender validade em 90 dias e mudar categoria
                nova_validade = date.today() + pd.Timedelta(days=90)
                st.session_state.inventario.at[idx, 'Validade'] = nova_validade
                st.session_state.inventario.at[idx, 'Categoria'] = "Congelador"
                guardar_dados(st.session_state.inventario)
                st.success(f"{row['Produto']} congelado e movido para o Congelador! Nova validade: {nova_validade.strftime('%d/%m/%Y')}")
                st.rerun()

    st.markdown("---")

    # Secção de Gestão de Itens (Expander para não ocupar muito espaço)
    with st.expander("🗑️ Gerir / Remover Itens"):
        item_para_remover = st.selectbox("Escolha um item para remover", df.index, format_func=lambda x: f"{df.loc[x, 'Produto']} ({df.loc[x, 'Categoria']})")
        if st.button("Remover Item Selecionado"):
            st.session_state.inventario = st.session_state.inventario.drop(item_para_remover).reset_index(drop=True)
            guardar_dados(st.session_state.inventario)
            st.success("Item removido!")
            st.rerun()

    # Opção radical para limpar toda a base de dados
    if st.button("Limpar Tudo (CUIDADO)"):
        st.session_state.inventario = pd.DataFrame(columns=["Produto", "Quantidade", "Categoria", "Validade"])
        guardar_dados(st.session_state.inventario)
        st.rerun()
else:
    st.info("O seu inventário está vazio. Adicione produtos na barra lateral!")

# Secção informativa para o utilizador com dicas de sustentabilidade
with st.expander("💡 Dicas para reduzir o desperdício"):
    st.write("""
    1. **Planeie as refeições:** Veja o que tem no AlgorithmicFresh antes de ir às compras.
    2. **Primeiro a entrar, primeiro a sair:** Coloque os itens mais antigos à frente no frigorífico.
    3. **Congele:** Muitos alimentos podem ser congelados se vir que não os vai consumir a tempo.
    4. **Organize por categorias:** Use as categorias para saber exatamente onde procurar os seus alimentos.
    """)
