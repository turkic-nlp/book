-- The PDF publication page is inserted before the preface via include-before-body.
-- Quarto lifts chapter headings out of conditional divs; suppress this HTML page's
-- heading as well as its conditionally hidden body to avoid an empty PDF chapter.
function Header(el)
  -- PDF and EPUB already insert the cover from their format settings.
  if not FORMAT:match("html") and el.identifier == "book-cover" then
    return {}
  end
  if FORMAT:match("latex") and el.identifier == "publication-details" then
    return {}
  end
end

-- The landing-page link/image is HTML-only; EPUB has its own packaged cover.
function RawBlock(el)
  if not FORMAT:match("html") and el.format == "html"
      and el.text:find('class="book-cover-page"', 1, true) then
    return {}
  end
end
