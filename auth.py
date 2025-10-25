import bcrypt
import streamlit as st
from database import SupabaseDB
from typing import Optional, Dict

class AuthManager:
    def __init__(self):
        self.db = SupabaseDB()
    
    def hash_password(self, password: str) -> str:
        """Gera hash da senha usando bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica se a senha corresponde ao hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            return False
    
    def login(self, email: str, password: str) -> Optional[Dict]:
        """Autentica usuário"""
        user = self.db.get_user_by_email(email)
        
        if user and self.verify_password(password, user['senha_hash']):
            # Remove senha do objeto de retorno por segurança
            user_data = {
                'id': user['id'],
                'nome': user['nome'],
                'email': user['email'],
                'papel': user['papel']
            }
            return user_data
        
        return None
    
    def is_logged_in(self) -> bool:
        """Verifica se há usuário logado na sessão"""
        return 'user' in st.session_state and st.session_state.user is not None
    
    def get_current_user(self) -> Optional[Dict]:
        """Retorna dados do usuário atual"""
        if self.is_logged_in():
            return st.session_state.user
        return None
    
    def logout(self):
        """Faz logout do usuário"""
        if 'user' in st.session_state:
            del st.session_state.user
        st.rerun()
    
    def require_login(self):
        """Força login se usuário não estiver autenticado"""
        if not self.is_logged_in():
            st.warning("⚠️ Você precisa fazer login para acessar esta página.")
            st.stop()
    
    def show_login_form(self):
        """Exibe formulário de login"""
        st.title("🔐 Sistema de Acompanhamento de Rotas")
        st.markdown("---")
        
        with st.form("login_form"):
            st.subheader("Login")
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            password = st.text_input("🔒 Senha", type="password", placeholder="Sua senha")
            submit = st.form_submit_button("🚀 Entrar", width='stretch')
            
            if submit:
                if not email or not password:
                    st.error("❌ Por favor, preencha todos os campos.")
                    return
                
                user = self.login(email, password)
                
                if user:
                    st.session_state.user = user
                    st.success(f"✅ Bem-vindo, {user['nome']}!")
                    st.rerun()
                else:
                    st.error("❌ Email ou senha incorretos.")
        
        # Informações de login de teste
        st.markdown("---")
        st.info("""
        **👤 Login de Teste:**
        - Email: admin@sistema.com
        - Senha: admin123
        """)