-- Allow long inline identifiers to wrap in PDF, including table captions.
function Code(el)
  if not FORMAT:match('latex') then return nil end
  local escaped = {['\\']='\\textbackslash{}', ['^']='\\textasciicircum{}', ['~']='\\textasciitilde{}'}
  local out = {}
  local has_arabic = false
  for _, cp in utf8.codes(el.text) do
    local c = utf8.char(cp)
    if cp >= 0x600 and cp <= 0x6ff then has_arabic = true end
    if escaped[c] then c=escaped[c]
    elseif c:match('[{}%%$&#_]') then c='\\' .. c end
    out[#out+1]=c
  end
  if has_arabic then
    return pandoc.RawInline('latex', '\\BookArabic{' .. table.concat(out, '') .. '}')
  end
  return pandoc.RawInline('latex', '\\texttt{' .. table.concat(out, '\\BookCodeBreak{}') .. '}')
end
function CodeBlock(el)
  if not FORMAT:match('latex') or #el.classes > 0 then return nil end
  return pandoc.RawBlock('latex', '\\begin{BookVerbatim}\n' .. el.text .. '\n\\end{BookVerbatim}')
end
function Link(el)
  if not FORMAT:match('latex') then return nil end
  local label = pandoc.utils.stringify(el.content)
  if label:match('^https?://') or label:match('^[%w.-]+%.[a-z]+/') then
    el.content = {Code(pandoc.Code(label))}
    return el
  end
end

function Str(el)
  if not FORMAT:match('latex') then return nil end
  for _, cp in utf8.codes(el.text) do
    if cp >= 0x600 and cp <= 0x6ff then
      local escaped = el.text:gsub('[%%$&#_{}]', function(c) return '\\' .. c end)
      return pandoc.RawInline('latex', '\\BookArabic{' .. escaped .. '}')
    end
  end
end
-- Narrow table cells need break opportunities in release IDs and long names.
function Table(el)
  if not FORMAT:match('latex') then return nil end
  return el:walk({Str = function(s)
    -- Only identifiers (digits, underscores, dots, slashes, colons) or very long
    -- strings get break points; ordinary words keep normal line breaking.
    local n = utf8.len(s.text)
    if n < 8 then return nil end
    if n < 18 and not s.text:match('[%d_%./:]') then
      -- zero glue lets TeX hyphenate a word that starts a narrow cell
      return {pandoc.RawInline('latex', '\\hspace{0pt}'), s}
    end
    local out = {}
    for _, cp in utf8.codes(s.text) do
      if cp >= 0x600 and cp <= 0x6ff then return nil end
      local c = utf8.char(cp)
      local escaped = {['\\']='\\textbackslash{}', ['^']='\\textasciicircum{}', ['~']='\\textasciitilde{}'}
      if escaped[c] then c=escaped[c]
      elseif c:match('[{}%%$&#_]') then c='\\' .. c end
      out[#out+1]=c
    end
    return pandoc.RawInline('latex',table.concat(out,'\\BookCodeBreak{}'))
  end})
end
