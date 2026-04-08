from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


PAPERS_ROOT = Path(__file__).resolve().parent
SBC_TEMPLATE = PAPERS_ROOT / "sbc-template.sty"
SBC_BST = PAPERS_ROOT / "sbc.bst"


ARTICLE_DIRS = [
    PAPERS_ROOT / "01_motivacao_e_negocio",
    PAPERS_ROOT / "02_fundamentos_de_rc",
    PAPERS_ROOT / "03_primeiro_modelo_previsao",
    PAPERS_ROOT / "04_memoria_nao_linearidade",
    PAPERS_ROOT / "05_avaliacao_e_boas_praticas",
    PAPERS_ROOT / "06_rc_fisico_e_ponte_para_qrc",
    PAPERS_ROOT / "07_qrc_para_previsao_de_demanda",
]


def latest_latex_dir(article_dir: Path) -> Path:
    candidates = sorted(path for path in article_dir.glob("latex_*") if path.is_dir())
    if not candidates:
        raise FileNotFoundError(f"nenhuma pasta latex_ encontrada em {article_dir}")
    return candidates[-1]


def normalize_tex(tex: str) -> str:
    lines = tex.splitlines()
    lines = [line[8:] if line.startswith("        ") else line for line in lines]
    normalized = "\n".join(lines).strip() + "\n"

    # Remove the workspace-specific template search path; the Overleaf package is self-contained.
    normalized = re.sub(
        r"\\makeatletter\s*\\def\\input@path\{\{\.\./\.\./\}\}\s*\\makeatother\s*",
        "",
        normalized,
        flags=re.MULTILINE,
    )
    return normalized


def build_readme(article_dir: Path, source_latex_dir: Path) -> str:
    return (
        f"# Pacote Overleaf\n\n"
        f"Este pacote foi gerado automaticamente a partir de `{source_latex_dir.name}`.\n\n"
        f"## Como usar no Overleaf\n\n"
        f"1. Envie todo o conteudo desta pasta para um projeto novo.\n"
        f"2. Defina `main.tex` como arquivo principal, se necessario.\n"
        f"3. Compile com `pdfLaTeX`.\n\n"
        f"## Conteudo\n\n"
        f"- `main.tex`: arquivo principal pronto para compilacao.\n"
        f"- `MANUSCRIPT.tex`: copia do manuscrito principal.\n"
        f"- `sbc-template.sty`: template da SBC.\n"
        f"- `sbc.bst`: estilo bibliografico SBC.\n"
        f"- `computational_results_*`: figuras e tabelas referenciadas no artigo.\n"
    )


def make_zip(package_dir: Path) -> Path:
    archive_base = str(package_dir)
    archive_path = shutil.make_archive(archive_base, "zip", root_dir=package_dir)
    return Path(archive_path)


def compile_package(package_dir: Path) -> None:
    for _ in range(2):
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "main.tex"],
            cwd=package_dir,
            capture_output=True,
        )
        if result.returncode not in (0, 1):
            raise RuntimeError(
                f"pdflatex falhou em {package_dir}\n"
                f"{result.stdout.decode('utf-8', errors='ignore')}\n"
                f"{result.stderr.decode('utf-8', errors='ignore')}"
            )

    pdf_path = package_dir / "main.pdf"
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF nao gerado em {package_dir}")


def cleanup_package(package_dir: Path) -> None:
    for name in ("main.aux", "main.log"):
        path = package_dir / name
        if path.exists():
            path.unlink()


def build_packages() -> dict[str, dict[str, str]]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    manifest: dict[str, dict[str, str]] = {}

    for article_dir in ARTICLE_DIRS:
        source_latex_dir = latest_latex_dir(article_dir)
        package_dir = article_dir / f"overleaf_{timestamp}"
        package_dir.mkdir(parents=True, exist_ok=False)

        source_tex = source_latex_dir / "MANUSCRIPT.tex"
        tex_content = normalize_tex(source_tex.read_text(encoding="utf-8"))
        (package_dir / "main.tex").write_text(tex_content, encoding="utf-8")
        (package_dir / "MANUSCRIPT.tex").write_text(tex_content, encoding="utf-8")

        shutil.copy2(SBC_TEMPLATE, package_dir / SBC_TEMPLATE.name)
        shutil.copy2(SBC_BST, package_dir / SBC_BST.name)

        for path in source_latex_dir.iterdir():
            if path.is_dir() and path.name.startswith("computational_results_"):
                shutil.copytree(path, package_dir / path.name)

        (package_dir / "README_OVERLEAF.md").write_text(
            build_readme(article_dir, source_latex_dir),
            encoding="utf-8",
        )

        compile_package(package_dir)
        cleanup_package(package_dir)
        zip_path = make_zip(package_dir)

        manifest[article_dir.name] = {
            "source_latex_dir": str(source_latex_dir),
            "overleaf_dir": str(package_dir),
            "zip": str(zip_path),
            "pdf": str(package_dir / "main.pdf"),
        }

    return manifest


def main() -> None:
    manifest = build_packages()
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
