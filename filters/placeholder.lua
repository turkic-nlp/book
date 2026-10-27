-- Render placeholders for missing data or experiments in red.
-- Inline:  [TO DO: run N1-1 audit]{.placeholder}
-- Block:   ::: {.placeholder}
--          Planned figure ... (experiment N2-1)
--          :::
-- HTML/EPUB: red text with a light red left border for blocks.
-- LaTeX/PDF: \textcolor{red}{...} / {\color{red} ...} (xcolor is loaded by Quarto).

local RED = "#C0001A"

local function is_ph(el)
  return el.classes:includes("placeholder")
end

function Span(el)
  if not is_ph(el) then return nil end
  if FORMAT:match("latex") then
    local out = { pandoc.RawInline("latex", "\\textcolor{red}{") }
    for _, c in ipairs(el.content) do table.insert(out, c) end
    table.insert(out, pandoc.RawInline("latex", "}"))
    return out
  elseif FORMAT:match("html") or FORMAT:match("epub") then
    el.attributes["style"] = "color:" .. RED .. ";"
    return el
  end
  return el.content
end

function Div(el)
  if not is_ph(el) then return nil end
  if FORMAT:match("latex") then
    local out = { pandoc.RawBlock("latex", "\\begingroup\\color{red}") }
    for _, b in ipairs(el.content) do table.insert(out, b) end
    table.insert(out, pandoc.RawBlock("latex", "\\endgroup"))
    return out
  elseif FORMAT:match("html") or FORMAT:match("epub") then
    el.attributes["style"] = "color:" .. RED .. "; border-left: 3px solid " .. RED ..
      "; padding: 0.4em 0.8em; margin: 1em 0; background: #FFF4F5;"
    return el
  end
  return el.content
end
