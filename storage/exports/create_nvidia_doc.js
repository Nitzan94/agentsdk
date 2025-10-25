const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign } = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: border, bottom: border, left: border, right: border };
const headerShading = { fill: "D5E8F0", type: ShadingType.CLEAR };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 1 } }
    ]
  },
  sections: [{
    properties: {
      page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
    },
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("NVIDIA Revenue Analysis FY2024-2026")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Overview")] }),
      new Paragraph({ children: [new TextRun("Analysis of NVIDIA Corporation revenue from Q2 FY2025 10-Q filing for period ending July 27, 2025.")] }),
      new Paragraph({ children: [new TextRun("")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Six-Month Revenue Comparison")] }),

      new Table({
        columnWidths: [3120, 3120, 3120],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, shading: headerShading,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Period", bold: true })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, shading: headerShading,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "H1 FY2026", bold: true })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, shading: headerShading,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "H1 FY2025", bold: true })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("Revenue")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$90,805M")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$56,084M")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("Growth")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "+62%", bold: true, color: "008000" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("-")] })] })
            ]
          })
        ]
      }),

      new Paragraph({ children: [new TextRun("")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Q2 Revenue Comparison")] }),

      new Table({
        columnWidths: [3120, 3120, 3120],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, shading: headerShading,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Period", bold: true })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, shading: headerShading,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Q2 FY2026", bold: true })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, shading: headerShading,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Q2 FY2025", bold: true })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("Revenue")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$46,743M")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$30,040M")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("Growth")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "+56%", bold: true, color: "008000" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("-")] })] })
            ]
          })
        ]
      }),

      new Paragraph({ children: [new TextRun("")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Revenue by Segment (H1 FY2026)")] }),

      new Table({
        columnWidths: [3120, 3120, 3120],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, shading: headerShading,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Segment", bold: true })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, shading: headerShading,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "H1 FY2026", bold: true })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA }, shading: headerShading,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Growth vs H1 FY2025", bold: true })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("Compute & Networking")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$80,920M")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "+65%", bold: true })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("Graphics")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$9,885M")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "+42%", bold: true })] })] })
            ]
          })
        ]
      }),

      new Paragraph({ children: [new TextRun("")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Revenue by Market (H1 FY2026)")] }),

      new Table({
        columnWidths: [4680, 4680],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, shading: headerShading,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Market", bold: true })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, shading: headerShading,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "H1 FY2026 Revenue", bold: true })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("Data Center")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$78,304M")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("Gaming")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$6,144M")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("Professional Visualization")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$2,162M")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("Automotive")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$2,095M")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("OEM & Other")] })] }),
              new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$2,100M")] })] })
            ]
          })
        ]
      }),

      new Paragraph({ children: [new TextRun("")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Key Highlights")] }),
      new Paragraph({ children: [new TextRun("Data Center revenue grew 64% YoY, driven by AI infrastructure demand for Hopper GPU computing platform and networking solutions.")] }),
      new Paragraph({ children: [new TextRun("")] }),
      new Paragraph({ children: [new TextRun("Customer Concentration: Two customers represented 20% and 15% of total revenue in H1 FY2026.")] }),
      new Paragraph({ children: [new TextRun("")] }),
      new Paragraph({ children: [new TextRun("Compute & Networking segment dominates at 89% of total revenue ($80.9B of $90.8B).")] })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("C:\\Users\\nitza\\devprojects\\personal-assistant\\NVIDIA_Revenue_Analysis.docx", buffer);
  console.log("Document created successfully: NVIDIA_Revenue_Analysis.docx");
});
