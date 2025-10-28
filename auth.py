import os
import bcrypt
import streamlit as st
from database import SupabaseDB
from typing import Optional, Dict


class AuthManager:
    """
    Gerencia autenticação: login, logout e registro.
    Compatível com app.py — inclui hash seguro de senhas e interface estilizada.
    """

    def __init__(self):
        self.db = SupabaseDB()
        self.session_key = "user"  # compatível com app principal

    # ========================================================
    # 🔐 Utilitários de senha
    # ========================================================
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    # ========================================================
    # 👤 Login / Registro
    # ========================================================
    def login(self, email: str, password: str) -> Optional[Dict]:
        user = self.db.get_user_by_email(email)
        if not user:
            return None
        stored_hash = user.get("senha_hash") or user.get("senha")
        if not stored_hash:
            return None
        if self.verify_password(password, stored_hash):
            return {
                "id": user.get("id"),
                "nome": user.get("nome"),
                "email": user.get("email"),
                "papel": user.get("papel", "usuario")
            }
        return None

    def register(self, nome: str, email: str, password: str, papel: str = "usuario") -> bool:
        # Validações básicas
        if not nome or not email or not password:
            return False

        # Se já existe usuário localmente, rejeita
        existing = self.db.get_user_by_email(email)
        if existing:
            return False

        # Preferimos criar a conta pelo Supabase Auth (sign_up) e deixar o trigger
        # no banco criar o perfil em app_..._usuarios. Isso evita problemas com RLS.
        try:
            # tentamos usar o client do supabase para criar a conta no Auth
            # quando disponível. A assinatura da função pode variar conforme a versão da lib.
            client = getattr(self.db, 'client', None)
            if client and hasattr(client, 'auth'):
                try:
                    # tenta a chamada padrão
                    client.auth.sign_up({"email": email, "password": password, "options": {"data": {"full_name": nome}}})
                except Exception:
                    # fallback: outra assinatura possível
                    try:
                        client.auth.sign_up(email=email, password=password, user_metadata={"full_name": nome})
                    except Exception:
                        # se falhar, prossegue para o método local (register_user)
                        raise

                # se sign_up conseguiu, retorna True (o trigger no banco cria o perfil)
                return True

        except Exception:
            # se qualquer erro ao usar Supabase Auth, voltamos ao método anterior
            pass

        # Caso o fluxo com Supabase Auth não esteja disponível ou falhe,
        # armazenamos senha hash localmente (legacy) — essa inserção pode falhar se RLS estiver ativo.
        senha_hash = self.hash_password(password)
        success = self.db.register_user(nome=nome, email=email, senha_hash=senha_hash, papel=papel)
        return success

    # ========================================================
    # 🧠 Sessão / estado
    # ========================================================
    def is_logged_in(self) -> bool:
        return self.session_key in st.session_state and st.session_state[self.session_key] is not None

    def get_current_user(self) -> Optional[Dict]:
        if self.is_logged_in():
            return st.session_state[self.session_key]
        return None

    def logout(self):
        if self.session_key in st.session_state:
            del st.session_state[self.session_key]
        st.rerun()

    # ========================================================
    # 💻 Interface de Login + Cadastro (corrigida com st.columns e use_container_width)
    # ========================================================
    def show_login_form(self):
        """Exibe a interface estilizada de login e cadastro usando colunas do Streamlit."""

        # Verifica se estamos no modo de reset de senha
        if st.session_state.get('show_reset', False):
            from password_reset import PasswordResetManager
            reset_manager = PasswordResetManager()
            reset_manager.show_reset_password_form()
            return

        # ----------- Carregar CSS externo -----------
        css_path = os.path.join("styles", "login.css")
        if os.path.exists(css_path):
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Arquivo 'styles/login.css' não encontrado. O layout pode ficar sem estilo.")

        # ----------- Usar colunas para layout estável -----------
        col_left, col_right = st.columns([1, 1], gap="large")

        # ----- Cabeçalho (título) e Caixa de Login/Cadastro (coluna esquerda) -----
        with col_left:
            # Título e subtítulo ficam fora da caixa (card) para que o card apareça abaixo do título
            st.markdown('<div class="auth-title">🚚 Sistema de Acompanhamento de Rotas</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-sub">Acesse sua conta ou crie um novo usuário</div>', unsafe_allow_html=True)

            # Agora abrimos o card que conterá as tabs e formulários
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            tabs = st.tabs(["🔑 Login", "📝 Cadastro"])

            # LOGIN
            with tabs[0]:
                with st.form("login_form"):
                    email = st.text_input("📧 Email", placeholder="seu@email.com")
                    password = st.text_input("🔒 Senha", type="password", placeholder="Sua senha")
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        submitted = st.form_submit_button("🚀 Entrar", use_container_width=True)
                    with col2:
                        if st.form_submit_button("Esqueci a senha", use_container_width=True):
                            st.session_state['show_reset'] = True
                            st.rerun()

                    if submitted:
                        if not email or not password:
                            st.error("❌ Preencha todos os campos.")
                        else:
                            user = self.login(email.strip().lower(), password)
                            if user:
                                st.session_state[self.session_key] = user
                                st.success(f"✅ Bem-vindo, {user.get('nome', 'Usuário')}!")
                                st.rerun()
                            else:
                                st.error("❌ Email ou senha incorretos.")

            # CADASTRO
            with tabs[1]:
                with st.form("register_form"):
                    nome = st.text_input("🧑 Nome completo", placeholder="Seu nome")
                    email_reg = st.text_input("📧 Email", placeholder="email@empresa.com")
                    password_reg = st.text_input("🔒 Senha", type="password", placeholder="Crie uma senha")
                    confirm = st.text_input("🔒 Confirme a senha", type="password", placeholder="Repita a senha")
                    submitted_reg = st.form_submit_button("Criar Conta")

                    if submitted_reg:
                        if not nome or not email_reg or not password_reg or not confirm:
                            st.error("❌ Preencha todos os campos.")
                        elif len(password_reg) < 6:
                            st.warning("⚠️ A senha deve ter pelo menos 6 caracteres.")
                        elif password_reg != confirm:
                            st.warning("⚠️ As senhas não coincidem.")
                        else:
                            success = self.register(nome.strip(), email_reg.strip().lower(), password_reg)
                            if success:
                                st.success("✅ Conta criada com sucesso!")
                                user = self.login(email_reg.strip().lower(), password_reg)
                                if user:
                                    st.session_state[self.session_key] = user
                                    st.rerun()
                            else:
                                st.error("❌ Este email já está cadastrado.")

            st.markdown('</div>', unsafe_allow_html=True)  # fecha auth-box

        # ----- Informações Adicionais (coluna direita) -----
        with col_right:
            st.markdown('<div class="welcome-box">', unsafe_allow_html=True)
            st.markdown('<h1>👋 Bem-vindo!</h1>', unsafe_allow_html=True)
            st.markdown("""
                <div class="welcome-text">
                    <p>Sistema de Acompanhamento de Rotas</p>
                    <ul>
                        <li>📊 Gestão eficiente de rotas</li>
                        <li>📱 Acesso em qualquer dispositivo</li>
                        <li>🔄 Atualizações em tempo real</li>
                        <li>📈 Relatórios detalhados</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
