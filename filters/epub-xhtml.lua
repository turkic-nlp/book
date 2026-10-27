-- Quarto puts fig-alt on its float wrapper as well as on the image.
-- XHTML permits alt on img, not div; retain the wrapper description as ARIA.
function Div(el)
  if FORMAT:match('epub') and el.attributes['alt'] then
    el.attributes['aria-label'] = el.attributes['alt']
    el.attributes['alt'] = nil
    return el
  end
end
