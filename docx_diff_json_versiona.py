import json
import uuid
import subprocess
import os

def convert_docx_to_json(docx_path, lua_filter_path):
    """Converte um DOCX para JSON usando Pandoc com o filtro Lua."""
    cmd = [
        "pandoc",
        docx_path,
        "--to=json",
        "--track-changes=all",
        f"--lua-filter={lua_filter_path}"
    ]
    print(f"Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao converter {docx_path}:")
        print(result.stderr)
        raise RuntimeError(f"Erro no Pandoc para {docx_path}")
    return json.loads(result.stdout)


def generate_diff_json(original_docx, modified_docx, lua_filter_path):
    original_json = convert_docx_to_json(original_docx, lua_filter_path)
    modified_json = convert_docx_to_json(modified_docx, lua_filter_path)

    # Implementação da lógica de comparação
    modificacoes = []
    for original_item, modified_item in zip(original_json.get("blocks", []), modified_json.get("blocks", [])):
        if original_item != modified_item:
            modificacoes.append({
                "id": str(uuid.uuid4()),
                "categoria": "alteracao",
                "conteudo": original_item,
                "alteracao": modified_item
            })

    diff_data = {
        "data": [
            {
                "versao": "V01",
                "status": "concluida",
                "modificacoes": modificacoes
            }
        ]
    }
    return json.dumps(diff_data, indent=4)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Uso: python docx_diff_json_versiona.py <original.docx> <modificado.docx> <lua_filter.lua>")
        sys.exit(1)

    original_doc = sys.argv[1]
    modified_doc = sys.argv[2]
    lua_filter = sys.argv[3]

    if not os.path.exists(lua_filter):
        print(f"ERRO: Filtro Lua não encontrado em '{lua_filter}'. Verifique o caminho.")
        sys.exit(1)

    json_output = generate_diff_json(original_doc, modified_doc, lua_filter)
    print(json_output)