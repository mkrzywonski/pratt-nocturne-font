# Design notes

Pratt Nocturne is an original vector interpretation of unusual handwriting. It preserves characteristic constructions while regularizing stroke weight and spacing. Missing characters are designed from related forms; they are not presented as recovered handwriting.

## Shared constructions

- **a / q:** a small detached head above a descending slash. The a uses a tiny T; the inferred q uses a boxy open c-shaped head and a slash shifted right.
- **e:** a closed eye with a short projection at the join, continuing into a long descent.
- **D / P / p:** related sweeping upper curves. D has a short detached inner stem; P has a longer stem. Lowercase p derives from P.
- **R / r:** distinct constructions. R has an upper enclosure, a projecting left serif and a straight diagonal leg. Lowercase r uses a short stem and rising branch.
- **h / k / b / l / i:** flagged or projecting entry details. Lowercase ascenders are intentionally shortened.
- **M / N / K:** connected but uneven strokes. Diagonals meet below the top of the left stem. K borrows the N stem and the diagonal gesture of R.
- **S / s / Z / z:** unequal upper and lower reach. Z/z use a mirrored-S influence with a firmer diagonal and a boxy lower turn.
- **o / O / Q / 0:** related rounded-box enclosures. Q has a steep short tail crossing the lower edge near the right side. Zero is shorter than the non-descending digits.
- **2 / 4 / 8 / 3:** a looped 2, broad open 4, and unequal compact bowls for 8. The inferred 3 borrows the right-hand curves of 8.
- **9:** a low, boxy loop and a long straight descender. This is an invented extension of the descending-vowel vocabulary.

## Family

Regular and Bold share constructions with different stroke widths. Oblique and Bold Oblique lean eight degrees, with individual bearing corrections. Mark anchors transform with their parent shapes.

All four faces contain 426 encoded characters and 475 glyphs. Their common vertical metrics allow room for accents and deep descenders. The fonts use a 1000-unit em.

## Evidence

The complete exemplar proof shows isolated source crops beside all four styles. Some source forms mix case, so uncertain assignments are marked. Related unaccented bases may inform accented characters; those are explicitly labeled as related forms rather than direct exemplars.

Original documents and identifying context are not distributed. Crop metadata records only a character, source category, image filename and uncertainty flag.

## Rendering and validation

The builder starts from explicit centerline paths, constructs mildly pressure-modulated ribbons, unions overlaps, and fits cubic Bézier contours. OTF retains cubic outlines; TTF and WOFF2 use quadratic outlines. OpenType rules provide selected kerning, deterministic alternates, common fraction substitutions and accent positioning.

Validation checks all twelve files with OpenType Sanitizer, confirms repertoire and metrics, and exercises shaping with HarfBuzz. The family is intended for expressive display use; it has no manual small-size hinting.
