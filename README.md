# Comparador de Documentos DOCX

---

Este projeto oferece uma solução eficaz para **comparar duas versões de um documento `.docx`** e visualizar as diferenças, incluindo alterações de texto e comentários, em um único arquivo HTML. Ele combina o poder do **Pandoc**, um **filtro Lua personalizado** e um script Python que usa o `difflib` para comparar as saídas HTML.

## Funcionalidades

* Compara dois arquivos `.docx` (original e modificado).
* Destaca **adições** (verde) e **remoções** (vermelho) de texto no HTML de saída.
* Inclui **comentários** inseridos no Word, exibindo o autor, data e conteúdo do comentário diretamente ao lado do texto comentado no HTML.
* Gera um arquivo HTML único e estilizado para fácil visualização em qualquer navegador.

## Como Funciona

A solução opera em três etapas principais, orquestradas pelo script Python `docx_diff_viewer.py`:

1.  **Conversão de DOCX para HTML (com filtro Lua):**
    * Para cada arquivo `.docx` de entrada, o script Python chama o **Pandoc**.
    * O Pandoc processa o `.docx` e aplica um **filtro Lua** (`comments_html_filter_direct.lua`). Este filtro é crucial; ele identifica os comentários do Word e **injeta suas informações (quem, quando, o quê)** diretamente no HTML como texto visível, formatado com classes CSS específicas.
    * O resultado são dois arquivos HTML temporários, um para o documento original e outro para o modificado, ambos contendo os comentários.

2.  **Comparação Textual dos HTMLs:**
    * O script Python lê as duas saídas HTML temporárias (do original e do modificado) linha por linha.
    * Utilizando a biblioteca padrão `difflib` do Python, ele compara o conteúdo dessas linhas HTML.
    * As diferenças (linhas adicionadas ou removidas) são identificadas.

3.  **Geração do HTML Final de Diferenças:**
    * Com base no resultado da comparação do `difflib`, o script constrói um novo arquivo HTML.
    * Ele envolve as linhas adicionadas em tags `<span>` com a classe `added` e as linhas removidas com a classe `removed`.
    * O **CSS embutido** no script Python (`style.css` foi integrado nele) é aplicado para colorir essas tags, tornando as alterações visualmente claras.
    * O resultado é um arquivo `diff_output.html` que pode ser aberto em qualquer navegador para revisão.

## Pré-requisitos

Para executar este projeto, você precisará ter o seguinte instalado em seu sistema:

* **Pandoc:** Ferramenta universal de conversão de documentos.
    * Instruções de instalação: [Pandoc Installation](https://pandoc.org/installing.html)
* **Python 3:** Linguagem de programação para o script principal.
    * Instruções de instalação: [Python.org](https://www.python.org/downloads/)

## Configuração e Instalação

Recomendamos o uso de um **ambiente virtual (venv)** para gerenciar as dependências do Python, garantindo que o projeto não interfira com outras instalações de Python em seu sistema.

1.  **Navegue até o diretório do projeto:**
    ```bash
    cd /caminho/para/o/seu/projeto/docx-compare
    ```

2.  **Crie e ative seu ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No macOS/Linux
    # ou
    .\venv\Scripts\activate    # No Windows
    ```

    *Nota: Certifique-se de que os arquivos `comments_html_filter_direct.lua` e `docx_diff_viewer.py` já estão no diretório do seu projeto. Não há um `requirements.txt` para este projeto, pois as dependências são mínimas e já nativas do Python.*

## Como Executar

Para comparar dois documentos `.docx` e gerar o HTML de diferenças:

1.  **Ative seu ambiente virtual** (se ainda não estiver ativo):
    ```bash
    source venv/bin/activate  # No macOS/Linux
    # ou
    .\venv\Scripts\activate    # No Windows
    ```

2.  **Execute o script Python:**
    ```bash
    python docx_diff_viewer.py <caminho_para_original.docx> <caminho_para_modificado.docx> <caminho_para_saida.html>
    ```

    **Exemplo:**

    ```bash
    python docx_diff_viewer.py documentos/relatorio_v1.docx documentos/relatorio_v2.docx resultado_comparacao.html
    ```

    Após a execução, um arquivo HTML (por exemplo, `resultado_comparacao.html`) será gerado no diretório especificado. Abra-o em seu navegador web preferido para visualizar as diferenças e os comentários.

3.  **Desativar o ambiente virtual (ao terminar):**
    Quando você finalizar suas tarefas com o projeto e quiser retornar ao seu ambiente Python padrão, execute:
    ```bash
    deactivate
    ```