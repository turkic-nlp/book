-- EPUB links must resolve inside the package. Source files remain companion assets.
function Link(el)
  if not FORMAT:match('epub') then return nil end
  local chapter = el.target:match('([^/]+)%.qmd$')
  if chapter then
    el.target = '#sec-book-' .. chapter
    return el
  end
  if not el.target:match('^%a[%w+.-]*:') and el.target:match('%.(.-)$') then
    if el.target:match('%.py$') or el.target:match('%.csv$')
      or el.target:match('%.ipynb$') or el.target:match('%.md$')
      or el.target:match('%.json$') then
      local path = el.target:gsub('^%.%./', '')
      local result = pandoc.Inlines(el.content)
      result:insert(pandoc.Str(' (companion source: '))
      result:insert(pandoc.Code(path))
      result:insert(pandoc.Str(')'))
      return result
    end
  end
end

-- Quarto places index.qmd first. Move the publication header and its
-- conditional content div ahead of the preface in the EPUB reading order.
function Pandoc(doc)
  if not FORMAT:match('epub') then return nil end
  for i,b in ipairs(doc.blocks) do
    if b.t == 'Header' and b.identifier == 'publication-details' then
      local body = doc.blocks[i+1]
      if not body or body.t ~= 'Div' then
        error('Expected the publication-details body immediately after its header')
      end
      body.content:insert(pandoc.Para({pandoc.Str(
        'Code and data paths in this edition refer to the companion book source tree; those files are not embedded in this EPUB.')}))
      doc.blocks:remove(i+1)
      doc.blocks:remove(i)
      doc.blocks:insert(1,body)
      doc.blocks:insert(1,b)
      return doc
    end
  end
  error('EPUB publication-details page is missing')
end

