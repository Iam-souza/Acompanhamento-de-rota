import pandas as pd
import streamlit as st
from typing import Dict, List, Any, Optional
import io
from datetime import datetime

class DataProcessor:
    
    @staticmethod
    def process_uploaded_file(uploaded_file) -> pd.DataFrame:
        """Processa arquivo CSV ou Excel enviado"""
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("❌ Formato de arquivo não suportado. Use CSV ou Excel.")
                return pd.DataFrame()
            
            return df
            
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def validate_required_columns(df: pd.DataFrame) -> bool:
        """Valida se o DataFrame possui as colunas obrigatórias"""
        required_columns = [
            'Data Cadastro', 'Os', 'Técnico', 'Supervisor'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Colunas obrigatórias ausentes: {', '.join(missing_columns)}")
            return False
        
        return True
    
    @staticmethod
    def prepare_data_for_insert(df: pd.DataFrame) -> List[Dict]:
        """Prepara dados do DataFrame para inserção no banco"""
        records = []
        
        # Mapeamento das colunas do arquivo para o banco de dados
        column_mapping = {
            'Data Cadastro': 'data_cadastro',
            'Serviço': 'servico',
            'Tipo de Serviço': 'tipo_servico',
            'Status Contrato': 'status',
            'Auditado': 'auditado',
            'Cop Reverteu': 'cop',
            'PDF': 'reverteu',
            'ENVIO PDF': 'pdf_envio',
            'Foto': 'pdf_foto_contrato',
            'Contrato': 'contrato',
            'WO': 'wo',
            'Os': 'os',
            'Cod. Status': 'cod_status',
            'COD': 'cod_cliente',
            'Cliente': 'cod_cliente',  # Alternativo
            'Técnico': 'tecnico',
            'Técnico Ofensor': 'tecnico_ofensor',
            'Login': 'login',
            'Supervisor': 'supervisor',
            'Matricula': 'matricula',
            'Cop': 'cop',
            'Local': 'local',
            'Habilidade de Trabalho': 'habilidade_trabalho',
            'Área de Trabalho': 'area_trabalho',
            'Ponto Casa/Apto.': 'ponto',
            'Cidade': 'cidade',
            'Base': 'base',
            'Periodo': 'periodo',
            'Inicio': 'inicio',
            'DESLOCAMENTO': 'deslocamento',
            'Fim': 'fim',
            'Tipo OS': 'tipo_os',
            'Grupo de Serviço': 'grupo_servico',
            'Endereço': 'endereco',
            'Número': 'numero',
            'Complemento': 'complemento',
            'Cep': 'cep',
            'Telefone 1': 'telefone1',
            'Telefone 2': 'telefone2',
            'Node': 'node',
            'Bairro': 'bairro',
            'Pacote': 'pacote',
            'Segmento': 'segmento',
            'OBS': 'obs',
            'OBS Técnico': 'obs_tecnico',
            'Ultimo usuário': 'ultimo_usuario'
        }
        
        for _, row in df.iterrows():
            record = {}
            
            for csv_col, db_col in column_mapping.items():
                if csv_col in df.columns:
                    value = row[csv_col]
                    # Converte NaN para None
                    if pd.isna(value):
                        record[db_col] = None
                    else:
                        # Tratamento especial para datas
                        if db_col in ['data_cadastro', 'inicio', 'fim']:
                            try:
                                if isinstance(value, str) and value.strip():
                                    # Tenta converter string para datetime
                                    record[db_col] = pd.to_datetime(value).strftime('%Y-%m-%d %H:%M:%S') if 'inicio' in db_col or 'fim' in db_col else pd.to_datetime(value).strftime('%Y-%m-%d')
                                elif pd.notna(value):
                                    record[db_col] = pd.to_datetime(value).strftime('%Y-%m-%d %H:%M:%S') if 'inicio' in db_col or 'fim' in db_col else pd.to_datetime(value).strftime('%Y-%m-%d')
                                else:
                                    record[db_col] = None
                            except:
                                record[db_col] = str(value) if pd.notna(value) else None
                        else:
                            record[db_col] = str(value) if not isinstance(value, (int, float)) else value
            
            records.append(record)
        
        return records
    
class DataProcessor:
    @staticmethod
    def export_to_excel(df: pd.DataFrame, filename: Optional[str] = None) -> bytes:
        """Exporta DataFrame para Excel"""
        if filename is None:
            filename = f"relatorio_consolidado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Relatório')
        
        return output.getvalue()
    
    @staticmethod
    def export_to_csv(df: pd.DataFrame) -> str:
        """Exporta DataFrame para CSV"""
        return df.to_csv(index=False)

class FilterManager:
    
    @staticmethod
    def create_date_filter():
        """Cria filtro de data"""
        col1, col2 = st.columns(2)
        
        with col1:
            data_inicio = st.date_input(
                "📅 Data Início",
                value=None,
                help="Selecione a data de início"
            )
        
        with col2:
            data_fim = st.date_input(
                "📅 Data Fim",
                value=None,
                help="Selecione a data de fim"
            )
        
        return data_inicio, data_fim
class UI:
    @staticmethod
    def create_select_filter(label: str, options: List[str], key: Optional[str] = None):
        """Cria filtro de seleção"""
        return st.selectbox(
            label,
            options=['Todos'] + options,
            key=key,
            help=f"Filtrar por {label.lower()}"
        )
    
    @staticmethod
    def create_text_filter(label: str, key: Optional[str] = None):
        """Cria filtro de texto"""
        return st.text_input(
            label,
            key=key,
            help=f"Buscar por {label.lower()}"
        )

class UIComponents:
    
    @staticmethod
    def show_user_info(user: Dict):
        """Exibe informações do usuário logado"""
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **{user['nome']}**")
        st.sidebar.markdown(f"📧 {user['email']}")
        st.sidebar.markdown(f"🏷️ {user['papel'].title()}")
    
    @staticmethod
    def show_logout_button(auth_manager):
        """Exibe botão de logout"""
        if st.sidebar.button("🚪 Sair", width='stretch'):
            auth_manager.logout()
    
    @staticmethod
    def show_stats(df: pd.DataFrame):
        """Exibe estatísticas dos dados"""
        if not df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Total de Registros", len(df))
            
            with col2:
                if 'tecnico' in df.columns:
                    st.metric("👷 Técnicos", df['tecnico'].nunique())
            
            with col3:
                if 'supervisor' in df.columns:
                    st.metric("👨‍💼 Supervisores", df['supervisor'].nunique())
            
            with col4:
                if 'tratativa' in df.columns:
                    resolvidos = len(df[df['tratativa'] == 'Resolvido'])
                    st.metric("✅ Resolvidos", resolvidos)