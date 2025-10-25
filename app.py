import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from auth import AuthManager
from database import SupabaseDB
from utils import DataProcessor, FilterManager, UIComponents

# Configuração da página
st.set_page_config(
    page_title="Sistema de Acompanhamento de Rotas",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização dos componentes
auth = AuthManager()
db = SupabaseDB()
processor = DataProcessor()
filter_manager = FilterManager()
ui = UIComponents()

def main():
    """Função principal da aplicação"""
    
    # Verifica se usuário está logado
    if not auth.is_logged_in():
        auth.show_login_form()
        return
    
    # Usuário logado - mostra aplicação principal
    user: Optional[Dict[str, Any]] = auth.get_current_user()
    
    # Sidebar com informações do usuário
    ui.show_user_info(user)
    ui.show_logout_button(auth)
    
    # Título principal
    st.title("🚚 Sistema de Acompanhamento de Rotas")
    st.markdown("---")
    
    # Tabs principais
    tab1, tab2, tab3 = st.tabs(["📤 Upload de Relatórios", "📊 Visualização e Edição", "📈 Análises"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_visualization_section()
    
    with tab3:
        show_analytics_section()

def show_upload_section():
    """Seção de upload de relatórios"""
    st.header("📤 Upload de Relatórios")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo CSV ou Excel",
        type=['csv', 'xlsx', 'xls'],
        help="Formatos suportados: CSV, Excel (.xlsx, .xls)"
    )
    
    if uploaded_file is not None:
        # Processa o arquivo
        df = processor.process_uploaded_file(uploaded_file)
        
        if not df.empty:
            st.success(f"✅ Arquivo carregado com sucesso! {len(df)} registros encontrados.")
            
            # Pré-visualização dos dados
            st.subheader("👀 Pré-visualização dos Dados")
            st.dataframe(df.head(10), width='stretch')
            
            # Validação das colunas
            if processor.validate_required_columns(df):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button("💾 Salvar Relatório", type="primary", key="save_report"):
                        save_report(df)
                
                with col2:
                    if st.button("🔄 Consolidar Dados", key="consolidate_data"):
                        consolidate_data()
            else:
                st.error("❌ Arquivo não possui as colunas obrigatórias necessárias.")
                st.info("""\
**📋 Colunas obrigatórias:**
- Data Cadastro
- Os
- Técnico  
- Supervisor
""")

def save_report(df: pd.DataFrame):
    """Salva relatório no banco de dados"""
    try:
        records = processor.prepare_data_for_insert(df)
        success_count = 0
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, record in enumerate(records):
            if db.insert_relatorio_raw(record):
                success_count += 1
            
            # Atualiza progresso
            progress = (i + 1) / len(records)
            progress_bar.progress(progress)
            status_text.text(f"Processando: {i + 1}/{len(records)}")
        
        progress_bar.empty()
        status_text.empty()
        
        if success_count > 0:
            st.success(f"✅ {success_count} registros salvos com sucesso!")
            
            # Auto-consolidação
            if st.button("🔄 Consolidar Automaticamente", key="auto_consolidate"):
                consolidate_data()
        else:
            st.error("❌ Nenhum registro foi salvo.")
            
    except Exception as e:
        st.error(f"❌ Erro ao salvar relatório: {str(e)}")

def consolidate_data():
    """Consolida dados brutos"""
    try:
        with st.spinner("🔄 Consolidando dados..."):
            consolidated_count = db.bulk_consolidate_from_raw()
        
        if consolidated_count > 0:
            st.success(f"✅ {consolidated_count} registros consolidados com sucesso!")
        else:
            st.info("ℹ️ Nenhum novo registro para consolidar.")
            
    except Exception as e:
        st.error(f"❌ Erro na consolidação: {str(e)}")

def show_visualization_section():
    """Seção de visualização e edição"""
    st.header("📊 Visualização e Edição de Dados")
    
    # Filtros
    with st.expander("🔍 Filtros", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            data_inicio, data_fim = filter_manager.create_date_filter()
        
        with col2:
            tecnicos = db.get_unique_values("tecnico")
            tecnico_filter = filter_manager.create_select_filter("👷 Técnico", tecnicos, key="tecnico_filter")
            
            supervisores = db.get_unique_values("supervisor")
            supervisor_filter = filter_manager.create_select_filter("👨‍💼 Supervisor", supervisores, key="supervisor_filter")
        
        with col3:
            cod_status_list = db.get_unique_values("cod_status")
            status_filter = filter_manager.create_select_filter("📋 Status", cod_status_list, key="status_filter")
            
            contrato_filter = filter_manager.create_text_filter("📄 Contrato", key="contrato_filter")
    
    # Monta filtros para consulta
    filters = {}
    if data_inicio:
        filters["data_inicio"] = data_inicio.strftime("%Y-%m-%d")
    if data_fim:
        filters["data_fim"] = data_fim.strftime("%Y-%m-%d")
    if tecnico_filter != "Todos":
        filters["tecnico"] = tecnico_filter
    if supervisor_filter != "Todos":
        filters["supervisor"] = supervisor_filter
    if status_filter != "Todos":
        filters["cod_status"] = status_filter
    if contrato_filter:
        filters["contrato"] = contrato_filter
    
    # Busca dados consolidados
    df = db.get_relatorios_consolidados(filters)
    
    if not df.empty:
        # Estatísticas
        ui.show_stats(df)
        st.markdown("---")
        
        # Configuração das colunas editáveis
        column_config = {
            "log": st.column_config.SelectboxColumn(
                "Log",
                options=list(range(1, 11)),
                required=False
            ),
            "certidao": st.column_config.SelectboxColumn(
                "Certidão",
                options=["Sim", "Não"],
                required=False
            ),
            "ativo": st.column_config.SelectboxColumn(
                "Ativo",
                options=["Com sucesso", "Sem sucesso"],
                required=False
            ),
            "tratativa": st.column_config.SelectboxColumn(
                "Tratativa",
                options=["Resolvido", "Não resolvido"],
                required=False
            ),
            "responsavel": st.column_config.SelectboxColumn(
                "Responsável",
                options=["CARLOS", "CINDI", "EDILENE", "EDUARDA", "IGOR", "MARCELO", "THIAGO"],
                required=False
            ),
            "data_cadastro": st.column_config.DateColumn(
                "Data Cadastro",
                format="DD/MM/YYYY"
            )
        }
        
        # Colunas desabilitadas para edição
        disabled_columns = [
            "id", "data_cadastro", "contrato", "os", "periodo", "cod_status",
            "tecnico", "supervisor", "area_trabalho", "node", "observacao_cop",
            "observacao_tecnico", "acao_trativa", "created_at", "updated_at", "updated_by"
        ]
        
        # Editor de dados
        st.subheader("✏️ Tabela Editável")
        edited_df = st.data_editor(
            df,
            column_config=column_config,
            disabled=disabled_columns,
            width='stretch',
            num_rows="dynamic"
        )
        
        # Botões de ação
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("💾 Salvar Alterações", type="primary", key="save_changes"):
                save_changes(df, edited_df)
        
        with col2:
            if st.button("📥 Exportar Excel", key="export_excel"):
                export_data(edited_df, "excel")
        
        with col3:
            if st.button("📥 Exportar CSV", key="export_csv"):
                export_data(edited_df, "csv")
    
    else:
        st.info("ℹ️ Nenhum dado encontrado com os filtros aplicados.")

def save_changes(original_df: pd.DataFrame, edited_df: pd.DataFrame):
    """Salva alterações na base de dados"""
    try:
        changes_count = 0
        
        # Compara DataFrames para identificar mudanças
        for idx, row in edited_df.iterrows():
            if idx < len(original_df):
                original_row = original_df.iloc[idx]
                
                # Verifica se houve mudanças nos campos editáveis
                editable_fields = ["log", "certidao", "ativo", "tratativa", "responsavel"]
                updates = {}
                
                for field in editable_fields:
                    if field in row and field in original_row:
                        if pd.isna(row[field]) and pd.isna(original_row[field]):
                            continue
                        elif row[field] != original_row[field]:
                            updates[field] = None if pd.isna(row[field]) else row[field]
                
                if updates:
                    if db.update_relatorio_consolidado(row["id"], updates):
                        changes_count += 1
        
        if changes_count > 0:
            st.success(f"✅ {changes_count} registros atualizados com sucesso!")
            st.rerun()
        else:
            st.info("ℹ️ Nenhuma alteração detectada.")
            
    except Exception as e:
        st.error(f"❌ Erro ao salvar alterações: {str(e)}")

def export_data(df: pd.DataFrame, format_type: str):
    """Exporta dados filtrados"""
    try:
        if format_type == "excel":
            excel_data = processor.export_to_excel(df)
            filename = f"relatorio_consolidado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        elif format_type == "csv":
            csv_data = processor.export_to_csv(df)
            filename = f"relatorio_consolidado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )
        
        st.success("✅ Arquivo preparado para download!")
        
    except Exception as e:
        st.error(f"❌ Erro ao exportar dados: {str(e)}")

def show_analytics_section():
    """Seção de análises e relatórios"""
    st.header("📈 Análises e Relatórios")
    
    # Busca todos os dados para análise
    df = db.get_relatorios_consolidados()
    
    if not df.empty:
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Geral", len(df))
        
        with col2:
            if 'tratativa' in df.columns:
                resolvidos = len(df[df['tratativa'] == 'Resolvido'])
                st.metric("✅ Resolvidos", resolvidos)
        
        with col3:
            if 'tratativa' in df.columns:
                nao_resolvidos = len(df[df['tratativa'] == 'Não resolvido'])
                st.metric("❌ Não Resolvidos", nao_resolvidos)
        
        with col4:
            if 'ativo' in df.columns:
                com_sucesso = len(df[df['ativo'] == 'Com sucesso'])
                st.metric("🎯 Com Sucesso", com_sucesso)
        
        st.markdown("---")
        
        # Gráficos de análise
        col1, col2 = st.columns(2)
        
        with col1:
            if 'tratativa' in df.columns:
                st.subheader("📊 Distribuição de Tratativas")
                tratativa_counts = df['tratativa'].value_counts()
                st.bar_chart(tratativa_counts)
        
        with col2:
            if 'responsavel' in df.columns:
                st.subheader("👥 Distribuição por Responsável")
                responsavel_counts = df['responsavel'].value_counts()
                st.bar_chart(responsavel_counts)
        
        # Tabela de resumo por técnico
        if 'tecnico' in df.columns:
            st.subheader("📋 Resumo por Técnico")
            
            summary = df.groupby('tecnico').agg({
                'id': 'count',
                'tratativa': lambda x: (x == 'Resolvido').sum(),
                'ativo': lambda x: (x == 'Com sucesso').sum()
            }).rename(columns={
                'id': 'Total',
                'tratativa': 'Resolvidos',
                'ativo': 'Com Sucesso'
            })
            
            st.dataframe(summary, width='stretch')
    
    else:
        st.info("ℹ️ Nenhum dado disponível para análise.")

if __name__ == "__main__":
    main()
