# Quick Start Guide - LinkedIn Content Automation

Este guia rápido te ajudará a configurar e executar o workflow em poucos minutos.

## ⚡ Setup Rápido (5 minutos)

### 1️⃣ Criar Repositório GitHub

```bash
# Navegue até o diretório do projeto
cd "d:/PC essentials/TESTES DE IA/Kestra Langchain Linkeding Content"

# Inicialize o Git
git init
git add .
git commit -m "Initial commit: LinkedIn automation with Kestra + LangChain 1.0"

# Crie um repositório no GitHub e conecte
git remote add origin https://github.com/SEU_USUARIO/linkedin-content-automation
git branch -M main
git push -u origin main
```

### 2️⃣ Atualizar Workflow com sua URL GitHub

Edite `linkedin-content-generator.yml` linha 39:
```yaml
url: https://github.com/SEU_USUARIO/linkedin-content-automation
```

### 3️⃣ Configurar Credenciais no Kestra

```bash
# Google Gemini API
kestra kv set GOOGLE_API_KEY "sua-chave-aqui"

# Brave Search API
kestra kv set BRAVE_SEARCH "sua-chave-aqui"

# LinkedIn Access Token
kestra kv set LINKEDIN_ACCESS_TOKEN "seu-token-aqui"

# Google Sheets (copie todo o JSON do service account)
kestra kv set GOOGLE_SHEETS_CREDENTIALS '{"type":"service_account","project_id":"...","private_key":"..."}'
```

### 4️⃣ Deploy no Kestra

```bash
# Validar sintaxe
kestra flow validate linkedin-content-generator.yml

# Fazer upload do workflow
kestra flow namespace update company.team linkedin-content-generator.yml
```

### 5️⃣ Testar Manualmente

1. Acesse o Kestra UI: `http://localhost:8080` (ou sua URL)
2. Navegue para `company.team` → `linkedin-content-generator`
3. Clique em **"Execute"**
4. Acompanhe os logs em tempo real

## 📋 Checklist de Credenciais

Antes de executar, certifique-se de ter:

- [ ] **Google API Key** - [Obter aqui](https://aistudio.google.com/app/apikey)
- [ ] **Brave Search API** - [Obter aqui](https://brave.com/search/api/)
- [ ] **LinkedIn App** criado com OAuth2 configurado
- [ ] **Google Sheets ID** correto (default: `1g7ZLdPYc8-XyKIexgHhpot8HTtcAv5uQmMXjBK4QUEo`)
- [ ] **Service Account** do Google Cloud com permissão no Sheet

## 🎯 Próxima Execução Agendada

Após o deploy, o workflow executará automaticamente:
- 🌅 **9:00 AM** (horário de Brasília)
- 🌞 **2:00 PM** (horário de Brasília)
- 🌆 **5:00 PM** (desabilitado por padrão - edite o workflow para ativar)

## 🐛 Troubleshooting Rápido

**Erro: `GOOGLE_API_KEY not found`**
→ Execute novamente o comando `kestra kv set GOOGLE_API_KEY "..."`

**Erro: `Failed to clone repository`**
→ Verifique se o repositório GitHub é público ou adicione credenciais de Git

**Imagem não gerada (NO_IMAGE)**
→ Normal! O workflow continua e publica apenas texto

**Não publicou no LinkedIn**
→ Verifique se o `LINKEDIN_ACCESS_TOKEN` ainda é válido (tokens expiram)

## 📊 Verificar Resultados

1. **LinkedIn**: Acesse seu perfil e veja o post publicado
2. **Google Sheets**: Abra a planilha e confira o novo tema adicionado
3. **Kestra Logs**: Revise os outputs de cada task

## 🎉 Pronto!

Seu workflow está configurado! Agora ele irá:
- ✅ Pesquisar tópicos trending em AI/Automation/Low-Code
- ✅ Gerar posts engajantes em inglês
- ✅ Criar imagens personalizadas
- ✅ Publicar automaticamente no LinkedIn
- ✅ Rastrear temas para evitar repetição

**Posts por mês**: Até 90 posts automáticos! 🚀
