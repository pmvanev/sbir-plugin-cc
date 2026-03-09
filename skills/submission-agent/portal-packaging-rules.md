---
name: portal-packaging-rules
description: Portal-specific packaging requirements for SBIR/STTR submission portals -- DSIP, Grants.gov, NSPIRES, and agency-specific portals. File naming, size limits, format requirements, and upload procedures.
---

# Portal Packaging Rules

## Portal Identification

Determine the submission portal from the solicitation metadata in proposal state (`topic.agency`) and solicitation text.

| Agency / Program | Portal | URL Pattern |
|-----------------|--------|-------------|
| DoD (all branches) | DSIP | https://www.dodsbirsttr.mil |
| Multi-agency (NSF, ED, DOT, EPA, SBA) | Grants.gov | https://www.grants.gov |
| NASA | NSPIRES | https://nspires.nasaprs.com |
| NIH / HHS | eRA Commons | https://commons.era.nih.gov |
| DOE | PAMS | https://pamspublic.science.energy.gov |
| DHS | SAM.gov / SBIR portal | Varies by solicitation |

When solicitation specifies a portal explicitly, use that -- it overrides agency defaults.

## DSIP (DoD SBIR/STTR)

### File Requirements
- **Technical Volume**: PDF, max 25 pages (Phase I) or as specified, 8.5x11 inches
- **Cost Volume**: PDF or Excel (.xlsx), no page limit but concise
- **Company Commercialization Report (CCR)**: Auto-generated from Company Registry, verify accuracy
- **Supporting Documents**: PDF format, per-topic attachment limits apply
- **Fraud/Waste/Abuse Training**: Certificate required, PDF

### Naming Convention
```
{TopicNumber}_{CompanyName}_{VolumeType}.pdf
Example: AF243-001_AcmeTech_TechnicalVolume.pdf
```

### Size Limits
- Individual file: 50 MB max
- Total submission package: varies by component

### Upload Procedure
1. Log in to DSIP portal
2. Navigate to open topic
3. Upload each volume in designated slot
4. System validates page count and file format
5. Submit -- system generates confirmation number
6. Download confirmation receipt

### Common Rejection Reasons
- Page count exceeds limit (cover page, TOC, references may or may not count -- check solicitation)
- Non-PDF technical volume
- Missing CCR (auto-populated but must be verified)
- Font size below minimum (often 10pt or 11pt)

## Grants.gov

### File Requirements
- **SF-424 (R&R)**: Required form set, completed in Workspace
- **Research & Related Budget**: Form-based entry
- **Technical Volume**: PDF attachment, page limits per solicitation
- **Biographical Sketches**: PDF, per-PI
- **Current & Pending Support**: Form or PDF per solicitation

### Naming Convention
```
{PI_LastName}_{DocumentType}.pdf
Example: Santos_TechnicalNarrative.pdf
```
- No special characters, no spaces (use underscores)
- Max filename length: 50 characters including extension

### Size Limits
- Individual attachment: 20 MB max
- Total package: no hard limit but keep reasonable

### Upload Procedure
1. Create Workspace for the funding opportunity
2. Complete all required forms
3. Upload PDF attachments in designated slots
4. Run "Check Package" validation
5. Submit through Authorized Organization Representative (AOR)
6. Track status in Grants.gov -- allow 24-48 hours for validation

### Common Rejection Reasons
- AOR not registered or SAM.gov registration expired
- Form fields incomplete or inconsistent
- PDF not meeting accessibility requirements (some agencies)
- Submission after deadline (Grants.gov timestamps are absolute)

## NSPIRES (NASA)

### File Requirements
- **Technical/Management Volume**: PDF, page limits per SBIR subtopic
- **Budget Justification**: PDF, no strict page limit
- **Commercialization Plan**: PDF (Phase II only)
- **Letters of Support**: Individual PDFs
- **Quad Chart**: PowerPoint (.pptx) or PDF, 1 page

### Naming Convention
```
{SubtopicNumber}_{CompanyName}_{Volume}.pdf
Example: H13.01_AcmeTech_Technical.pdf
```

### Size Limits
- Individual file: 50 MB
- Quad chart: 1 page, 1 MB recommended

### Upload Procedure
1. Register in NSPIRES, link to institution
2. Create proposal shell under target subtopic
3. Complete cover page and budget forms
4. Upload volume PDFs in designated sections
5. Validate -- system checks required fields
6. Submit -- generates proposal number

### Common Rejection Reasons
- Institution not linked in NSPIRES
- Missing quad chart
- Page count violation (NASA counts from page 1 of narrative, excluding cover)
- Budget form inconsistency with justification narrative

## Pre-Submission Verification Checklist

Universal checks before any portal submission:

### File Integrity
- [ ] All PDF files open without error
- [ ] No password protection on any file
- [ ] Page counts within solicitation limits
- [ ] Font sizes meet minimum requirements
- [ ] All figures/images render correctly in PDF

### Content Completeness
- [ ] Every required volume/attachment present
- [ ] All forms completed (if form-based submission)
- [ ] Budget numbers consistent across volumes
- [ ] Company name consistent across all documents
- [ ] PI name and credentials consistent
- [ ] DUNS/UEI number matches SAM.gov registration

### Compliance Cross-Check
- [ ] Compliance matrix items all addressed (covered or waived with reason)
- [ ] File naming matches portal convention
- [ ] File sizes within portal limits
- [ ] Required certifications and representations included

### Deadline Safety
- [ ] Submission attempted minimum 24 hours before deadline
- [ ] Portal account access verified (login test)
- [ ] AOR availability confirmed (Grants.gov only)
- [ ] Backup submission plan documented if portal issues

## Archive Requirements

After submission, create an immutable snapshot:

### Archive Structure
```
artifacts/wave-8-submission/
  submission-manifest.md        # File list, checksums, portal, timestamp
  submitted/                    # Exact copies of submitted files
    {filename1}.pdf
    {filename2}.pdf
    ...
  confirmation/
    confirmation-receipt.md     # Portal confirmation number, timestamp
    screenshot.png              # If available
```

### Manifest Format
```markdown
# Submission Manifest

- **Portal**: {portal name}
- **Submitted At**: {ISO-8601 timestamp}
- **Confirmation Number**: {portal-generated ID}
- **Topic**: {topic ID} -- {topic title}
- **Submitted By**: {user name}

## Files Submitted

| File | Size | SHA-256 | Portal Slot |
|------|------|---------|-------------|
| {name} | {size} | {hash} | {slot description} |
```

### Immutability Rule
Once the submission manifest records a confirmation number, the `artifacts/wave-8-submission/submitted/` directory and its contents are frozen. PES enforces this -- any write attempt to the submitted archive triggers a block.
