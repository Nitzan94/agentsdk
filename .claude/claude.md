## File Organization

**Project-Based Structure** - Each task/project gets dedicated folder:

storage/projects/<project-name>/
  - All related files together (reports, spreadsheets, docs, research)
  - Example: storage/projects/nvidia-analysis/ contains revenue report, financial model, notes
  - Example: storage/projects/mcdonalds-market-research/ contains competitive analysis, presentation

**Naming:**
- Project folders: lowercase-with-dashes (nvidia-analysis, q4-planning)
- Files within: descriptive names (revenue_report.md, financial_model.xlsx)

**Quick tasks/standalone docs:**
- storage/content/ - Blog posts, articles, one-off content
- storage/notes/ - General notes, quick captures

Always use full paths: Write("storage/projects/nvidia-analysis/revenue_report.md", content)

## Workflow

1. Clarify before assuming
2. Use Write tool with proper folder path based on content type
3. Track sources in research with analyze_research tool
4. Create structured documents when needed (reports, summaries)
5. Use Skills for complex document creation (spreadsheets, presentations)