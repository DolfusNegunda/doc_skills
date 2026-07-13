# Logo Swap Procedure (Organization-Agnostic)

A `.docx` file is a zip archive. In every base template used by this skill family, the swappable logo lives at the first header image — by convention `word/media/image1.*`.

Always convert the new logo image to match the existing `image1` extension (jpeg vs png) before replacing it inside the zip. See the reference implementation in `authoring-lessons-learned-docs/scripts/generate_lessons_learned.py`.

## Verification
After swapping, extract `word/media/image1.*` from the output `.docx` and visually inspect it at least once per new organization's template.
