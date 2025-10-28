# Checklist de Segurança

## 1. Autenticação e Autorização
- [ ] Verificar se todas as rotas sensíveis estão protegidas por autenticação
- [ ] Confirmar se as políticas RLS (Row Level Security) do Supabase estão corretamente configuradas
- [ ] Validar se os tokens JWT estão sendo gerenciados de forma segura
- [ ] Implementar proteção contra força bruta nos endpoints de login
- [ ] Verificar se as senhas estão sendo hasheadas antes de serem armazenadas
- [ ] Implementar tempo de expiração adequado para as sessões

## 2. Gerenciamento de Credenciais
- [ ] Remover todas as credenciais hardcoded do código fonte
- [ ] Verificar se todas as chaves sensíveis estão em arquivos .env
- [ ] Confirmar se o arquivo .env está no .gitignore
- [ ] Rotacionar periodicamente as chaves de API e senhas
- [ ] Utilizar secrets manager em ambiente de produção
- [ ] Verificar se as chaves de serviço (service_role) estão protegidas

## 3. Segurança de Dados
- [ ] Implementar validação de entrada em todos os campos
- [ ] Verificar proteção contra SQL Injection
- [ ] Implementar sanitização de dados antes do armazenamento
- [ ] Confirmar se dados sensíveis estão sendo criptografados
- [ ] Implementar backup regular dos dados
- [ ] Verificar se logs não contêm informações sensíveis

## 4. Segurança da Aplicação
- [ ] Implementar CORS corretamente
- [ ] Adicionar headers de segurança (HSTS, CSP, X-Frame-Options)
- [ ] Verificar proteção contra XSS
- [ ] Implementar rate limiting nos endpoints
- [ ] Manter todas as dependências atualizadas
- [ ] Realizar scan regular de vulnerabilidades

## 5. Upload de Arquivos
- [ ] Validar tipos de arquivos permitidos
- [ ] Implementar limite de tamanho para uploads
- [ ] Verificar se os arquivos são armazenados de forma segura
- [ ] Sanitizar nomes de arquivos
- [ ] Implementar varredura de malware em uploads (se aplicável)

## 6. Monitoramento e Logs
- [ ] Implementar logging de eventos de segurança
- [ ] Configurar alertas para atividades suspeitas
- [ ] Manter logs de acesso e alterações
- [ ] Implementar monitoramento de performance
- [ ] Configurar logging de erros apropriado

## 7. Configuração de Ambiente
- [ ] Verificar configurações de segurança do Streamlit
- [ ] Configurar firewalls adequadamente
- [ ] Manter sistema operacional e software base atualizados
- [ ] Desabilitar recursos não utilizados
- [ ] Implementar backups automáticos

## 8. Documentação
- [ ] Documentar procedimentos de segurança
- [ ] Manter registro de incidentes de segurança
- [ ] Documentar processo de recuperação de desastres
- [ ] Manter documentação de configuração atualizada
- [ ] Criar guia de boas práticas de segurança para desenvolvedores

## 9. Compliance e Privacidade
- [ ] Verificar conformidade com LGPD
- [ ] Implementar política de privacidade
- [ ] Documentar processamento de dados pessoais
- [ ] Implementar mecanismo de consentimento do usuário
- [ ] Criar processo para solicitações de dados pessoais

## Ações Imediatas Prioritárias
1. [ ] Rotacionar todas as chaves expostas no código
2. [ ] Implementar ambiente de staging para testes
3. [ ] Realizar auditoria de segurança inicial
4. [ ] Revisar todas as políticas RLS
5. [ ] Implementar logging completo de eventos

## Revisão Periódica
- [ ] Agendar revisão mensal desta checklist
- [ ] Realizar testes de penetração regulares
- [ ] Atualizar documentação de segurança
- [ ] Revisar e atualizar políticas de acesso
- [ ] Realizar treinamento de segurança da equipe