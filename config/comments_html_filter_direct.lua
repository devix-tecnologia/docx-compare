-- comments_html_filter.lua

-- Função para processar Spans (trechos de texto com atributos)
function Span (elem)
  -- Verifica se o Span tem a classe 'comment' e um atributo 'data-comment-text'
  if elem.classes:includes('comment') then
    local comment_text = elem.attributes['data-comment-text'] or 'Conteúdo do comentário não disponível.'
    local comment_author = elem.attributes['data-comment-author'] or 'Autor desconhecido.'
    local comment_date = elem.attributes['data-comment-date'] or 'Data desconhecida.' -- Pandoc pode ou não expor isso diretamente
    local comment_id = elem.attributes['id'] or 'sem-id' -- ID interno do comentário

    -- Para o "onde", não temos uma informação de localização exata no texto via atributo,
    -- mas o comentário está semanticamente "onde o Span está".
    -- Poderíamos usar o ID ou uma referência visual.

    -- Construir o conteúdo HTML para o tooltip/popup
    local comment_html_content = pandoc.Inlines {
      pandoc.Str("Quem: "), pandoc.Strong(pandoc.Str(comment_author)), pandoc.LineBreak(),
      pandoc.Str("Quando: "), pandoc.Str(comment_date), pandoc.LineBreak(),
      pandoc.Str("O Quê: "), pandoc.Str(comment_text)
      -- Onde: Poderíamos adicionar uma anotação aqui se tivéssemos um ID de parágrafo, por exemplo.
    }

    -- Criar um Span HTML que envolva o texto original e inclua as informações do comentário
    -- Usaremos atributos customizados (data-*) para armazenar os detalhes
    -- e uma classe para facilitar o estilo e scripts JS/CSS para exibir o tooltip/popup
    local new_span = pandoc.Span(elem.content, {
      id = comment_id,
      classes = {"document-comment"}, -- Uma classe para estilização e JS
      attributes = {
        ['data-comment-author'] = comment_author,
        ['data-comment-date'] = comment_date,
        ['data-comment-text'] = comment_text
      }
    })

    return new_span
  end
  
  -- Se não for um comentário, retorna o elemento Span inalterado
  return elem
end