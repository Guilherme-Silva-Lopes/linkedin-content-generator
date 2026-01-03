# ⚠️ IMPORTANTE: Este arquivo contém APENAS exemplos de configuração

Este arquivo `.env.example` é um **template de documentação** e não contém nenhuma credencial real.

## 🔐 Sobre Segurança

- ✅ **Todos os valores são placeholders genéricos** (`your-*-here`)
- ✅ **Nenhuma credencial real está commitada** neste repositório
- ✅ **Este arquivo é seguro para versionar** no Git

## 📋 Como Usar

1. **NÃO use este arquivo diretamente**
2. **NÃO crie um arquivo `.env`** neste repositório (ele está no `.gitignore`)
3. **Configure as credenciais diretamente no Kestra KV Store**:

```bash
# Exemplo de configuração no Kestra
kestra kv set GOOGLE_API_KEY "sua-chave-real-aqui"
kestra kv set BRAVE_SEARCH "sua-chave-real-aqui"
kestra kv set LINKEDIN_ACCESS_TOKEN "seu-token-real-aqui"
kestra kv set GOOGLE_SHEETS_CREDENTIALS '{"type":"service_account",...}'
```

## 🚨 Alerta de Segurança do GitHub

Se você recebeu um alerta do GitHub sobre "secrets detected", isso é um **falso positivo**.

O GitHub detecta padrões que se parecem com API keys, mas os valores neste arquivo são apenas exemplos de formato, não credenciais reais:

- `your-google-api-key-here` ← Placeholder genérico
- `your-brave-search-api-key-here` ← Placeholder genérico  
- `your-linkedin-access-token-here` ← Placeholder genérico

## ✅ Ação Necessária

**Nenhuma ação necessária!** Este repositório está seguro. Todas as credenciais reais devem ser configuradas apenas no Kestra KV Store, nunca no código versionado.

## 📚 Mais Informações

Ver README.md seção "🔧 Setup Instructions" para instruções completas de configuração.
