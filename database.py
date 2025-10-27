import os
from supabase import create_client, Client
import pandas as pd
from typing import Optional, List, Dict, Any
import streamlit as st

class SupabaseDB:
    """
    Wrapper leve para operações com Supabase que seu app usa.
    - Mantive as tabelas e métodos existentes.
    - Adicionei `register_user` para o fluxo de cadastro.
    """

    def __init__(self):
        # Substitua as variáveis de ambiente ou mantenha as strings se você já estiver usando assim.
        self.url = os.getenv("SUPABASE_URL", "https://bekjfhrfpmuxrgcsbyns.supabase.co")
        self.key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJla2pmaHJmcG11eHJnZ3NieW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMjM2MTYsImV4cCI6MjA3Njg5OTYxNn0.70A7KcikrTLGZMZO3APTnURNfYXOL2nB6Q4cbgprPBE")
        self.client: Client = create_client(self.url, self.key)

        # Tabelas existentes no seu projeto
        self.table_usuarios = "app_0c87e04f3a_usuarios"
        self.table_relatorios_raw = "app_0c87e04f3a_relatorios_raw"
        self.table_relatorios_consolidados = "app_0c87e04f3a_relatorios_consolidados"

    # -----------------------------
    # Usuários
    # -----------------------------
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email (retorna dict ou None)."""
        try:
            response = self.client.table(self.table_usuarios).select("*").eq("email", email).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            st.error(f"Erro ao buscar usuário: {str(e)}")
            return None

    def register_user(self, nome: str, email: str, senha_hash: str, papel: str = "usuario") -> bool:
        """
        Insere novo usuário na tabela. Espera que a coluna para senha seja 'senha_hash'.
        Retorna True se inserido com sucesso, False caso email já exista ou erro.
        """
        try:
            # Verifica duplicidade
            existing = self.client.table(self.table_usuarios).select("id").eq("email", email).execute()
            if existing.data:
                return False

            payload = {
                "nome": nome,
                "email": email,
                "senha_hash": senha_hash,
                "papel": papel
            }
            self.client.table(self.table_usuarios).insert(payload).execute()
            return True
        except Exception as e:
            st.error(f"Erro ao registrar usuário: {str(e)}")
            return False

    # -----------------------------
    # Relatórios (mantive suas funções)
    # -----------------------------
    def insert_relatorio_raw(self, data: Dict) -> bool:
        try:
            self.client.table(self.table_relatorios_raw).insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Erro ao inserir relatório bruto: {str(e)}")
            return False

    def insert_relatorio_consolidado(self, data: Dict) -> bool:
        try:
            existing = self.client.table(self.table_relatorios_consolidados) \
                .select("id") \
                .eq("contrato", data.get("contrato")) \
                .eq("os", data.get("os")) \
                .execute()

            if not existing.data:
                self.client.table(self.table_relatorios_consolidados).insert(data).execute()
                return True
            else:
                return False
        except Exception as e:
            st.error(f"Erro ao inserir relatório consolidado: {str(e)}")
            return False

    def get_relatorios_consolidados(self, filters: Dict = None) -> pd.DataFrame:
        try:
            query = self.client.table(self.table_relatorios_consolidados).select("*")

            if filters:
                if filters.get("data_inicio") and filters.get("data_fim"):
                    query = query.gte("data_cadastro", filters["data_inicio"]) \
                                 .lte("data_cadastro", filters["data_fim"])

                if filters.get("tecnico"):
                    query = query.eq("tecnico", filters["tecnico"])

                if filters.get("supervisor"):
                    query = query.eq("supervisor", filters["supervisor"])

                if filters.get("cod_status"):
                    query = query.eq("cod_status", filters["cod_status"])

                if filters.get("contrato"):
                    query = query.ilike("contrato", f"%{filters['contrato']}%")

            response = query.execute()
            if response.data:
                df = pd.DataFrame(response.data)
                if "data_cadastro" in df.columns:
                    df["data_cadastro"] = pd.to_datetime(df["data_cadastro"])
                return df
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Erro ao buscar relatórios consolidados: {str(e)}")
            return pd.DataFrame()

    def update_relatorio_consolidado(self, record_id: str, updates: Dict) -> bool:
        try:
            # Se quiser usar timestamp real do Postgres, deixe o banco aplicar default.
            updates["updated_at"] = "now()"
            self.client.table(self.table_relatorios_consolidados).update(updates).eq("id", record_id).execute()
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar relatório: {str(e)}")
            return False

    def get_unique_values(self, column: str, table: str = None) -> List[str]:
        try:
            if table is None:
                table = self.table_relatorios_consolidados

            response = self.client.table(table).select(column).execute()
            if response.data:
                values = [item[column] for item in response.data if item.get(column) is not None]
                return sorted(list(set(values)))
            return []
        except Exception as e:
            st.error(f"Erro ao buscar valores únicos: {str(e)}")
            return []

    def consolidate_data(self, raw_data: Dict) -> Dict:
        consolidated = {
            "data_cadastro": raw_data.get("data_cadastro"),
            "contrato": raw_data.get("contrato"),
            "os": raw_data.get("os"),
            "periodo": raw_data.get("periodo"),
            "cod_status": raw_data.get("cod_status"),
            "tecnico": raw_data.get("tecnico"),
            "supervisor": raw_data.get("supervisor"),
            "area_trabalho": raw_data.get("area_trabalho"),
            "node": raw_data.get("node"),
            "observacao_cop": raw_data.get("obs"),
            "observacao_tecnico": raw_data.get("obs_tecnico"),
            "acao_trativa": None,
            "log": None,
            "certidao": None,
            "ativo": None,
            "tratativa": None,
            "responsavel": None
        }
        return consolidated

    def bulk_consolidate_from_raw(self) -> int:
        try:
            raw_response = self.client.table(self.table_relatorios_raw).select("*").execute()
            if not raw_response.data:
                return 0

            consolidated_count = 0
            for raw_record in raw_response.data:
                consolidated_data = self.consolidate_data(raw_record)
                if self.insert_relatorio_consolidado(consolidated_data):
                    consolidated_count += 1
            return consolidated_count
        except Exception as e:
            st.error(f"Erro na consolidação em lote: {str(e)}")
            return 0
