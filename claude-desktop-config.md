# Claude Desktop Configuration Guide

**Purpose:** Fast AI-assisted development environment setup for this project  
**Date:** June 20, 2026

---

## Claude Desktop MCP Configuration

Claude Desktop supports Model Context Protocol (MCP) servers for enhanced capabilities.

### Configuration File Location

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

---

## Recommended MCP Servers for This Project

### 1. **Filesystem Access** (Built-in)
For reading/writing design documents:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "D:\\code_ai\\code\\project-designs"]
    }
  }
}
```

### 2. **PostgreSQL Database** (For Schema Design)

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/design_db"]
    }
  }
}
```

### 3. **Web Search** (For Latest Tech Info)

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 4. **GitHub Integration**

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

---

## Complete Configuration Example

**File:** `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "D:\\code_ai\\code\\project-designs"
      ]
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost:5432/design_db"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "BSA..."
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
      }
    }
  },
  "globalShortcut": "Ctrl+Space"
}
```

---

## Alternative: Cursor IDE Configuration

### `.cursorrules` File

Create `.cursorrules` in project root:

```markdown
# AI Coding Rules for Cursor IDE

You are an expert in designing production-ready AI/ML platforms.

## Tech Stack (June 2026)
- Backend: Golang 1.22+ + Python 3.12+
- Frontend: Next.js 16 + React 19.2.7
- AI: GPT-5.5, Claude Opus 4.8
- Database: PostgreSQL 16 + pgvector + Redis 7
- Python: HTTPX, asyncio, dataclasses, Logfire, uv, Ruff
- Security: PASETO (NOT JWT)

## Design Principles
1. Production-first: 99.9% uptime SLA
2. TDD: 85%+ test coverage
3. Security: PASETO, rate limiting, input validation
4. Modern patterns: async/await, dataclasses, type hints

## Code Style

### Python
- Use `httpx` not `requests`
- Use `uv` not `pip`
- Use dataclasses for models
- Use `logfire` for observability
- Always type hint
- Always async for I/O

### Golang
- Use Fiber framework
- Proper error handling
- Context propagation
- Structured logging

### TypeScript/React
- Functional components
- React 19.2.7 patterns
- TypeScript strict mode
- Server components where possible

## Security Rules
- ALWAYS use PASETO (never JWT)
- ALWAYS validate input
- ALWAYS rate limit APIs
- ALWAYS use prepared statements
- ALWAYS encrypt sensitive data

## When Creating Design Docs
Include: Executive Summary, Architecture, Tech Stack, Implementation, Schema, Guardrails, TDD Strategy

## Mermaid Diagrams
Test compatibility with v11.6.0+. Include: sequence, flowchart, state, ER diagrams.
```

---

## Windsurf IDE Configuration

### `.windsurfrules` File

```yaml
# Windsurf AI Rules
project_type: ai_ml_design_documents
language: [python, golang, typescript]
framework: [fastapi, fiber, nextjs]

rules:
  - name: use_latest_versions
    description: Always use latest versions (June 2026)
    versions:
      nextjs: "16.x"
      react: "19.2.7"
      python: "3.12+"
      golang: "1.22+"
      
  - name: modern_python
    patterns:
      - use: httpx
        instead_of: requests
      - use: uv
        instead_of: pip
      - use: dataclasses
        instead_of: dict
        
  - name: security_first
    requirements:
      - paseto_tokens: true
      - rate_limiting: true
      - input_validation: true
      - encryption: true
      
  - name: tdd_required
    min_coverage: 85
    test_first: true
    
code_style:
  python:
    formatter: ruff
    linter: ruff
    type_checker: pyright
    
  golang:
    formatter: gofmt
    linter: golangci-lint
    
  typescript:
    formatter: prettier
    linter: eslint
```

---

## VS Code Configuration

### `.vscode/settings.json`

```json
{
  "ai.rules": "file://.clinerules",
  "python.defaultInterpreterPath": "uv",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff",
  "go.useLanguageServer": true,
  "go.lintTool": "golangci-lint",
  "typescript.tsdk": "node_modules/typescript/lib",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true,
    "source.organizeImports": true
  },
  "files.associations": {
    ".clinerules": "markdown",
    ".cursorrules": "markdown"
  }
}
```

---

## GitHub Copilot Configuration

### `.github/copilot-instructions.md`

```markdown
# GitHub Copilot Instructions

This repository contains enterprise-grade AI/ML platform designs.

## Context
- Production-ready designs (99.9% SLA)
- TDD approach (85%+ coverage)
- Latest tech stack (June 2026)

## Tech Stack
Backend: Golang 1.22+ + Python 3.12+
Frontend: Next.js 16 + React 19.2.7
AI: GPT-5.5, Claude Opus 4.8
DB: PostgreSQL 16 + pgvector + Redis 7

## Code Preferences
Python: httpx, asyncio, dataclasses, logfire, uv
Golang: Fiber, proper errors, context
React: Functional, hooks, server components

## Security
ALWAYS: PASETO tokens, input validation, rate limiting, encryption

## When Suggesting Code
- Include type hints
- Include error handling
- Include tests
- Include docstrings
- Follow modern patterns
```

---

## Quick Setup Script

### Windows PowerShell

```powershell
# Create Claude Desktop config
$configPath = "$env:APPDATA\Claude"
New-Item -ItemType Directory -Path $configPath -Force

$config = @"
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "D:\\code_ai\\code\\project-designs"]
    }
  }
}
"@

$config | Out-File -FilePath "$configPath\claude_desktop_config.json" -Encoding UTF8

Write-Host "✅ Claude Desktop configured!"
```

### macOS/Linux Bash

```bash
#!/bin/bash

# Create Claude Desktop config
mkdir -p ~/Library/Application\ Support/Claude

cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json <<EOF
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "$HOME/code_ai/code/project-designs"]
    }
  }
}
EOF

echo "✅ Claude Desktop configured!"
```

---

## Testing Your Configuration

### 1. Verify MCP Servers

After restarting Claude Desktop:

```
Ask Claude: "What MCP servers are available?"
```

### 2. Test Filesystem Access

```
Ask Claude: "List all design documents in the project-designs folder"
```

### 3. Test Code Generation

```
Ask Claude: "Generate a FastAPI endpoint using the modern Python patterns from .clinerules"
```

---

## Troubleshooting

### MCP Server Not Loading

1. Check Node.js is installed: `node --version`
2. Check npx works: `npx --version`
3. Restart Claude Desktop completely
4. Check config file syntax (valid JSON)

### Permission Issues

**Windows:**
```powershell
icacls "D:\code_ai\code\project-designs" /grant Users:F
```

**macOS/Linux:**
```bash
chmod -R 755 ~/code_ai/code/project-designs
```

### API Key Issues

Get API keys from:
- **Brave Search**: https://brave.com/search/api/
- **GitHub**: https://github.com/settings/tokens

---

## Best Practices

1. **Keep configs in sync** across all AI tools (.clinerules, .cursorrules, etc.)
2. **Version control** your AI rules (commit .clinerules)
3. **Document changes** when updating tech stack versions
4. **Test regularly** to ensure AI assistants follow your rules
5. **Share with team** for consistent AI-assisted development

---

**Status:** ✅ Complete Configuration Guide  
**Version:** 1.0  
**Date:** June 20, 2026  
**Compatible With:** Claude Desktop, Cursor, Windsurf, VS Code, GitHub Copilot
