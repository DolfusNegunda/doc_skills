# Org Onboarding Checklist

Run through this whenever deploying a document-type skill at a new organization for the first time.

## 1. Determine the starting point
- [ ] Ask whether the organization has an existing branded Word document of this type. If yes, that becomes the base template.
- [ ] If no existing document: use the document-type skill's shared generic neutral template.

## 2. If reusing the organization's own document
- [ ] Copy the file — never edit the organization's original.
- [ ] Confirm it contains the standard section headings verbatim.
- [ ] Identify the swappable logo image inside the document.
- [ ] Replace existing single-value text with `{{TOKEN}}` placeholders (`{{PROJECT_NAME}}`, `{{PROJECT_CODE}}`, `{{PROJECT_MANAGER}}`, `{{COVER_DATE}}`, `{{METADATA_DATE}}`, `{{ORG_NAME}}`) where appropriate.

## 3. If starting from the shared generic template
- [ ] Ask for the organization's logo image only.
- [ ] Optionally ask if they want their organization name inserted into the footer/header text beyond the `{{ORG_NAME}}` token.

## 4. Save the profile
- [ ] Store the finished base template and logo together clearly.

## 5. Test before real use
- [ ] Run the document-type skill's generation script with a small, clearly-fake test data set.
- [ ] Run the full validation checklist in `docx-editing-patterns.md` against the test output.
