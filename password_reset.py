import streamlit as st
from database import SupabaseDB

class PasswordResetManager:
    def __init__(self):
        self.db = SupabaseDB()

    def request_reset(self, email: str) -> bool:
        """Envia email de reset de senha para o usuário"""
        try:
            # Usa o client do Supabase para enviar o email de reset
            self.db.client.auth.reset_password_email(email)
            return True
        except Exception as e:
            st.error(f"Erro ao enviar email de reset: {str(e)}")
            return False

    def show_reset_password_form(self):
        """Exibe o formulário de solicitação de reset de senha"""
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)
        
        st.markdown("### 🔑 Recuperação de Senha")
        st.markdown("Digite seu email para receber as instruções de recuperação de senha.")
        
        with st.form("reset_password_form"):
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            submitted = st.form_submit_button("Enviar Link de Recuperação")
            
            if submitted:
                if not email:
                    st.error("❌ Por favor, digite seu email.")
                else:
                    if self.request_reset(email.strip().lower()):
                        st.success("✅ Email de recuperação enviado! Verifique sua caixa de entrada.")
                        st.info("ℹ️ Verifique também sua pasta de spam se não encontrar o email.")
                    else:
                        st.error("❌ Não foi possível enviar o email de recuperação.")
        
        # Link para voltar ao login
        st.markdown("---")
        if st.button("← Voltar ao Login"):
            st.session_state['show_reset'] = False
            st.experimental_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)