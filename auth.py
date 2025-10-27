import bcrypt
import streamlit as st
from database import SupabaseDB
from typing import Optional, Dict

class AuthManager:
    """
    Gerencia autenticação: login, logout e registro.
    Interface compatível com o app.py existente:
      - is_logged_in()
      - get_current_user()
      - logout()
      - show_login_form()
    """

    def __init__(self):
        self.db = SupabaseDB()
        self.session_key = "user"  # compatível com seu app.py atual

    # -----------------------------
    # Utilitários de senha
    # -----------------------------
    def hash_password(self, password: str) -> str:
        """Gera hash da senha usando bcrypt (salt automático). Retorna string decodificada."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica senha usando bcrypt. hashed deve ser str (decodificado)."""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    # -----------------------------
    # Login / Registro
    # -----------------------------
    def login(self, email: str, password: str) -> Optional[Dict]:
        """
        Autentica usuário. Retorna dicionário do usuário sem o hash de senha em caso de sucesso.
        É esperado que a tabela de usuários tenha a coluna 'senha_hash'.
        """
        user = self.db.get_user_by_email(email)
        if not user:
            return None

        stored_hash = user.get("senha_hash") or user.get("senha")  # tentativa de compatibilidade
        if not stored_hash:
            return None

        if self.verify_password(password, stored_hash):
            # monta objeto seguro (remove hash)
            user_data = {
                "id": user.get("id"),
                "nome": user.get("nome"),
                "email": user.get("email"),
                "papel": user.get("papel", "usuario")
            }
            return user_data

        return None

    def register(self, nome: str, email: str, password: str, papel: str = "usuario") -> bool:
        """
        Cria novo usuário. Retorna True se criado com sucesso, False caso contrário.
        """
        # Verificações simples
        if not nome or not email or not password:
            return False

        # Verifica se já existe
        existing = self.db.get_user_by_email(email)
        if existing:
            return False

        senha_hash = self.hash_password(password)
        success = self.db.register_user(nome=nome, email=email, senha_hash=senha_hash, papel=papel)
        return success

    # -----------------------------
    # Sessão / estado
    # -----------------------------
    def is_logged_in(self) -> bool:
        return self.session_key in st.session_state and st.session_state[self.session_key] is not None

    def get_current_user(self) -> Optional[Dict]:
        if self.is_logged_in():
            return st.session_state[self.session_key]
        return None

    def logout(self):
        if self.session_key in st.session_state:
            del st.session_state[self.session_key]
        st.experimental_rerun()

    # -----------------------------
    # UI: formulário Login + Cadastro
    # -----------------------------
def show_login_form(self):
    import os

    logo_path = os.path.join("uploads_img", "logo_via.png")

    # CSS para estilização
    st.markdown(
        """
        <style>
        .auth-box {
            max-width: 400px;
            padding: 2rem;
            border-radius: 14px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);
            background: linear-gradient(180deg, #ffffff 0%, #fbfbfd 100%);
        }
        .auth-title {
            text-align: center;
            font-weight: 700;
            font-size: 20px;
            margin-bottom: 6px;
            color: #111827;
        }
        .auth-sub {
            text-align: center;
            color: #6b7280;
            margin-bottom: 1.2rem;
            font-size: 13px;
        }
        .small-note { font-size:12px; color:#6b7280; text-align:center; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Divide a tela em colunas
    col1, col2 = st.columns([1, 2])  # col1 menor para o formulário à esquerda

    with col1:
        st.image(logo_path, width=200)
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)
        st.markdown('<div class="auth-title">🚚 Sistema de Acompanhamento de Rotas</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Acesse sua conta ou crie um novo usuário</div>', unsafe_allow_html=True)

        tabs = st.tabs(["🔑 Login", "📝 Cadastro"])

        # ---------- LOGIN ----------
        with tabs[0]:
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="seu@email.com")
                password = st.text_input("🔒 Senha", type="password", placeholder="Sua senha")
                submitted = st.form_submit_button("🚀 Entrar")

                if submitted:
                    if not email or not password:
                        st.error("❌ Preencha todos os campos.")
                    else:
                        user = self.login(email.strip().lower(), password)
                        if user:
                            st.session_state[self.session_key] = user
                            st.success(f"✅ Bem-vindo, {user.get('nome','Usuário')}!")
                            st.experimental_rerun()
                        else:
                            st.error("❌ Email ou senha incorretos.")

            st.markdown('<p class="small-note">Conta de teste: admin@sistema.com / admin123</p>', unsafe_allow_html=True)

        # ---------- CADASTRO ----------
        with tabs[1]:
            with st.form("register_form"):
                nome = st.text_input("🧑 Nome completo", placeholder="Seu nome")
                email_reg = st.text_input("📧 Email", placeholder="email@empresa.com")
                password_reg = st.text_input("🔒 Senha", type="password", placeholder="Crie uma senha (mínimo 6 caracteres)")
                confirm = st.text_input("🔒 Confirme a senha", type="password", placeholder="Repita a senha")
                submitted_reg = st.form_submit_button("Criar Conta")

                if submitted_reg:
                    if not nome or not email_reg or not password_reg or not confirm:
                        st.error("❌ Preencha todos os campos.")
                    elif len(password_reg) < 6:
                        st.warning("⚠️ A senha deve ter ao menos 6 caracteres.")
                    elif password_reg != confirm:
                        st.warning("⚠️ As senhas não coincidem.")
                    else:
                        success = self.register(nome=nome.strip(), email=email_reg.strip().lower(), password=password_reg)
                        if success:
                            st.success("✅ Conta criada com sucesso! Você já pode fazer login.")
                            user = self.login(email_reg.strip().lower(), password_reg)
                            if user:
                                st.session_state[self.session_key] = user
                                st.experimental_rerun()
                        else:
                            st.error("❌ Email já em uso.")

        st.markdown('</div>', unsafe_allow_html=True)
  # fecha auth-box

        # Logo à direita
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image("Uploads_img/Logo da VIA Serviços Integrados.png")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # fecha auth-container
