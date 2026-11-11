"""Baixa os dados brutos do estudo METR (Becker et al., 2025) numa versão fixa.

A base não declara licença, por isso o repositório da equipe NÃO redistribui o
arquivo: este script o baixa do repositório original, fixado no commit usado no
artigo, e confere o hash SHA-256.

Uso:  python baixar_dados.py
"""
import hashlib
import pathlib
import urllib.request

COMMIT = "7ff2d7670235f531dff77eff58355bd77392f396"
URL = (
    "https://raw.githubusercontent.com/METR/Measuring-Early-2025-AI-on-Exp-OSS-Devs/"
    f"{COMMIT}/data_complete.csv"
)
SHA256_ESPERADO = "1493fc46dc379b15d2c39273fa7a7ee98767ff0d90dea113f300d7338f165746"
DESTINO = pathlib.Path(__file__).parent / "dados" / "brutos" / "data_complete.csv"


def main() -> None:
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as resp:
        conteudo = resp.read()
    sha = hashlib.sha256(conteudo).hexdigest()
    if sha != SHA256_ESPERADO:
        raise SystemExit(f"Hash diferente do esperado ({sha}); arquivo de origem mudou?")
    DESTINO.write_bytes(conteudo)
    print(f"OK: {DESTINO} ({len(conteudo)} bytes, sha256={sha[:12]}...)")


if __name__ == "__main__":
    main()
