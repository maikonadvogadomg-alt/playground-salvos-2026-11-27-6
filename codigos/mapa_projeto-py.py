import os
import re
import json
import sys

# Pasta a analisar: a pasta onde o script está, ou a informada na linha de comando
PASTA = sys.argv[1] if len(sys.argv) > 1 else "."
SAIDA = "mapa_projeto.txt"

# Pastas que não precisam ser lidas (são grandes e geradas automaticamente)
IGNORAR = {"node_modules", ".git", "dist", "build", ".next"}

# Tipos de arquivo que serão analisados por dentro
EXTENSOES_CODIGO = {".ts", ".tsx", ".js", ".jsx", ".html", ".css", ".py"}

# Procura linhas como: import algo from "arquivo" ou require("arquivo")
padrao_import = re.compile(r"""(?:from\s+|import\s+|require\()\s*['"]([^'"]+)['"]""")
padrao_replit = re.compile(r"replit|repl\.co", re.IGNORECASE)

# 1. Lista todos os arquivos
todos = []
for raiz, pastas, nomes in os.walk(PASTA):
    pastas[:] = [p for p in pastas if p not in IGNORAR]
    for nome in nomes:
        todos.append(os.path.join(raiz, nome))

linhas = []
linhas.append(f"MAPA DO PROJETO: {os.path.abspath(PASTA)}")
linhas.append(f"Total de arquivos lidos: {len(todos)}")
linhas.append("")

# 2. Lista de arquivos com tamanho
linhas.append("== ARQUIVOS ==")
for caminho in sorted(todos):
    tamanho = os.path.getsize(caminho) / 1024
    linhas.append(f"{os.path.relpath(caminho, PASTA)}  ({tamanho:.1f} KB)")
linhas.append("")

# 3. Comandos do package.json (o que o botão "bate" executa)
linhas.append("== COMANDOS (package.json) ==")
for caminho in todos:
    if os.path.basename(caminho) == "package.json":
        try:
            with open(caminho, encoding="utf-8", errors="ignore") as f:
                dados = json.load(f)
            for nome, comando in dados.get("scripts", {}).items():
                linhas.append(f"{nome}: {comando}")
        except Exception as erro:
            linhas.append(f"Não consegui ler package.json: {erro}")
linhas.append("")

# 4. Quem importa quem, e arquivos que citam Replit
linhas.append("== IMPORTAÇÕES E REFERÊNCIAS A REPLIT ==")
for caminho in sorted(todos):
    if os.path.splitext(caminho)[1] not in EXTENSOES_CODIGO:
        continue
    with open(caminho, encoding="utf-8", errors="ignore") as f:
        texto = f.read()
    linhas.append(f"\n{os.path.relpath(caminho, PASTA)}")
    for imp in sorted(set(padrao_import.findall(texto))):
        linhas.append(f"   importa: {imp}")
    if padrao_replit.search(texto):
        linhas.append("   ATENÇÃO: cita Replit")

# Salva o relatório (não altera nenhum arquivo do projeto)
with open(SAIDA, "w", encoding="utf-8") as f:
    f.write("\n".join(linhas))

print(f"Pronto. Relatório salvo em: {SAIDA}")
