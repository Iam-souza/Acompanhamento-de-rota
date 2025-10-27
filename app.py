import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any
from auth import AuthManager
from database import SupabaseDB
from utils import DataProcessor, FilterManager, UIComponents

# -----------------------------
# Configuração da página
# -----------------------------
st.set_page_config(
    page_title="Via Representações",
    page_icon="Logo da Via Serviços Integrados.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Inicialização dos componentes
# -----------------------------
auth = AuthManager()
db = SupabaseDB()
processor = DataProcessor()
filter_manager = FilterManager()
ui = UIComponents()

# -----------------------------
# Função principal
# -----------------------------
def main():
    if not auth.is_logged_in():
        auth.show_login_form()
        return

    user: Optional[Dict[str, Any]] = auth.get_current_user()
    st.sidebar.markdown(f"**Usuário logado:** {user.get('nome', '')}")
    if st.sidebar.button("🔒 Logout"):
        auth.logout()

    st.title("🚚 Sistema de Acompanhamento de Rotas")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📤 Upload", "📊 Visualização", "📈 Análises"])
    
    with tab1:
        show_upload_section()
    with tab2:
        show_visualization_section()
    with tab3:
        show_analytics_section()

# -----------------------------
# Seção Upload
# -----------------------------
def show_upload_section():
    st.header("📤 Upload de Relatórios")
    uploaded_file = st.file_uploader(
        "Selecione arquivo CSV ou Excel",
        type=['csv', 'xlsx', 'xls']
    )

    if uploaded_file is not None:
        df = processor.process_uploaded_file(uploaded_file)
        if df.empty:
            st.warning("Arquivo vazio ou inválido!")
            return
        
        st.success(f"✅ {len(df)} registros encontrados.")
        st.dataframe(df.head(10), width='stretch')

        if not processor.validate_required_columns(df):
            st.error("Arquivo não possui colunas obrigatórias.")
            return

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salvar Relatório"):
                save_report(df)
        with col2:
            if st.button("🔄 Consolidar Dados"):
                consolidate_data()

def save_report(df: pd.DataFrame):
    try:
        records = processor.prepare_data_for_insert(df)
        progress_bar = st.progress(0)
        status_text = st.empty()
        success_count = 0

        for i, record in enumerate(records):
            if db.upsert_relatorio_raw(record):
                success_count += 1
            progress_bar.progress((i + 1) / len(records))
            status_text.text(f"Processando {i + 1}/{len(records)}")

        progress_bar.empty()
        status_text.empty()
        st.success(f"✅ {success_count} registros salvos/atualizados!")

    except Exception as e:
        st.error(f"Erro ao salvar relatório: {e}")

def consolidate_data():
    try:
        with st.spinner("🔄 Consolidando dados..."):
            count = db.bulk_consolidate_from_raw()
        st.success(f"✅ {count} registros consolidados!")
    except Exception as e:
        st.error(f"Erro na consolidação: {e}")

# -----------------------------
# Seção Visualização
# -----------------------------
def show_visualization_section():
    st.header("📊 Visualização e Edição")
    with st.expander("🔍 Filtros", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            data_inicio, data_fim = filter_manager.create_date_filter()
        with col2:
            tecnico = ui.create_select_filter("👷 Técnico", db.get_unique_values("tecnico"), key="tecnico")
            supervisor = ui.create_select_filter("👨‍💼 Supervisor", db.get_unique_values("supervisor"), key="supervisor")
        with col3:
            status = ui.create_select_filter("📋 Status", db.get_unique_values("cod_status"), key="status")
            contrato = ui.create_text_filter("📄 Contrato", key="contrato")

    filters = {}
    if data_inicio: filters["data_inicio"] = data_inicio.strftime("%Y-%m-%d")
    if data_fim: filters["data_fim"] = data_fim.strftime("%Y-%m-%d")
    if tecnico != "Todos": filters["tecnico"] = tecnico
    if supervisor != "Todos": filters["supervisor"] = supervisor
    if status != "Todos": filters["cod_status"] = status
    if contrato: filters["contrato"] = contrato

    df = db.get_relatorios_consolidados(filters)
    if df.empty:
        st.info("ℹ️ Nenhum dado encontrado.")
        return

    ui.show_stats(df)
    st.markdown("---")

    # Colunas editáveis
    column_config = ui.get_column_config()
    disabled_columns = ui.get_disabled_columns()

    edited_df = st.data_editor(
        df,
        column_config=column_config,
        disabled=disabled_columns,
        width='stretch',
        num_rows="dynamic"
    )

    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button("💾 Salvar Alterações"):
            save_changes(df, edited_df)
    with col2:
        if st.button("📥 Exportar Excel"):
            export_data(edited_df, "excel")
    with col3:
        if st.button("📥 Exportar CSV"):
            export_data(edited_df, "csv")

def save_changes(original_df: pd.DataFrame, edited_df: pd.DataFrame):
    try:
        changes_count = 0
        editable_fields = ["log","certidao","ativo","tratativa","responsavel"]
        for idx, row in edited_df.iterrows():
            original_row = original_df.iloc[idx]
            updates = {f: row[f] for f in editable_fields if row[f] != original_row[f]}
            if updates and db.update_relatorio_consolidado(row["id"], updates):
                changes_count += 1
        st.success(f"✅ {changes_count} registro(s) atualizado(s)!")
    except Exception as e:
        st.error(f"Erro ao salvar alterações: {e}")

def export_data(df: pd.DataFrame, file_type: str):
    try:
        if file_type == "excel":
            content = processor.export_to_excel(df)
            st.download_button("📥 Baixar Excel", content, f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            content = processor.export_to_csv(df)
            st.download_button("📥 Baixar CSV", content, f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")
    except Exception as e:
        st.error(f"Erro ao exportar: {e}")

# -----------------------------
# Seção Análises
# -----------------------------
def show_analytics_section():
    st.header("📈 Análises")
    st.info("🔹 Em desenvolvimento. Dashboards e gráficos virão aqui.")

# -----------------------------
# Executa app
# -----------------------------
if __name__ == "__main__":
    main()
