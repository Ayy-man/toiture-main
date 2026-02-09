import {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  WidthType,
  AlignmentType,
  HeadingLevel,
  BorderStyle,
} from "docx";
import type { HybridQuoteResponse, WorkItem, PricingTier } from "@/types/hybrid-quote";
import { fr } from "@/lib/i18n/fr";
import { en } from "@/lib/i18n/en";

// Format number as CAD currency (French Canadian format)
function formatCAD(amount: number): string {
  return new Intl.NumberFormat("fr-CA", {
    style: "currency",
    currency: "CAD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export async function generateQuoteDOCX(
  quote: HybridQuoteResponse,
  category: string,
  sqft: number,
  date: string,
  locale: "fr" | "en" = "fr"
): Promise<Blob> {
  // Get translations for the current locale
  const t = locale === "fr" ? fr : en;

  // Get Standard tier for pricing
  const standardTier = quote.pricing_tiers.find(
    (tier) => tier.tier === "Standard"
  ) as PricingTier;

  const doc = new Document({
    sections: [
      {
        properties: {},
        children: [
          // Header - Title
          new Paragraph({
            text: locale === "fr" ? "SOUMISSION" : "QUOTE",
            heading: HeadingLevel.HEADING_1,
            alignment: AlignmentType.CENTER,
            spacing: { after: 100 },
          }),

          // Header - Subtitle
          new Paragraph({
            children: [
              new TextRun({
                text: "Toiture LV",
                color: "666666",
              }),
            ],
            alignment: AlignmentType.CENTER,
            spacing: { after: 300 },
          }),

          // Job Info - Date
          new Paragraph({
            children: [
              new TextRun({
                text: "Date: ",
                bold: true,
              }),
              new TextRun({
                text: date,
              }),
            ],
            spacing: { after: 100 },
          }),

          // Job Info - Category
          new Paragraph({
            children: [
              new TextRun({
                text: locale === "fr" ? "Categorie: " : "Category: ",
                bold: true,
              }),
              new TextRun({
                text: category,
              }),
            ],
            spacing: { after: 100 },
          }),

          // Job Info - Area
          new Paragraph({
            children: [
              new TextRun({
                text: locale === "fr" ? "Superficie: " : "Area: ",
                bold: true,
              }),
              new TextRun({
                text: `${sqft.toLocaleString("fr-CA")} ${locale === "fr" ? "pi2" : "sq ft"}`,
              }),
            ],
            spacing: { after: 300 },
          }),

          // Work Items Section Header
          new Paragraph({
            children: [
              new TextRun({
                text: locale === "fr" ? "TRAVAUX" : "WORK ITEMS",
                bold: true,
              }),
            ],
            spacing: { before: 200, after: 200 },
            border: {
              bottom: {
                color: "333333",
                space: 1,
                style: BorderStyle.SINGLE,
                size: 6,
              },
            },
          }),

          // Work Items - Bullet List (NO HOURS - client facing)
          ...quote.work_items.map(
            (item: WorkItem) =>
              new Paragraph({
                text: item.name,
                bullet: {
                  level: 0,
                },
                spacing: { after: 100 },
              })
          ),

          // Summary Section Header
          new Paragraph({
            children: [
              new TextRun({
                text: locale === "fr" ? "SOMMAIRE" : "SUMMARY",
                bold: true,
              }),
            ],
            spacing: { before: 300, after: 200 },
            border: {
              bottom: {
                color: "333333",
                space: 1,
                style: BorderStyle.SINGLE,
                size: 6,
              },
            },
          }),

          // Summary Table
          new Table({
            width: {
              size: 100,
              type: WidthType.PERCENTAGE,
            },
            borders: {
              top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              insideHorizontal: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
              insideVertical: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
            },
            rows: [
              // Materials Row
              new TableRow({
                children: [
                  new TableCell({
                    children: [
                      new Paragraph({
                        text: locale === "fr" ? "Materiaux" : "Materials",
                      }),
                    ],
                    borders: {
                      top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                    },
                  }),
                  new TableCell({
                    children: [
                      new Paragraph({
                        text: formatCAD(standardTier.materials_cost),
                        alignment: AlignmentType.RIGHT,
                      }),
                    ],
                    borders: {
                      top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                    },
                  }),
                ],
              }),

              // Labor Row
              new TableRow({
                children: [
                  new TableCell({
                    children: [
                      new Paragraph({
                        text: locale === "fr" ? "Main-d'oeuvre" : "Labor",
                      }),
                    ],
                    borders: {
                      top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                    },
                  }),
                  new TableCell({
                    children: [
                      new Paragraph({
                        text: formatCAD(standardTier.labor_cost),
                        alignment: AlignmentType.RIGHT,
                      }),
                    ],
                    borders: {
                      top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                    },
                  }),
                ],
              }),

              // Total Row (with top border)
              new TableRow({
                children: [
                  new TableCell({
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun({
                            text: "TOTAL",
                            bold: true,
                          }),
                        ],
                      }),
                    ],
                    borders: {
                      top: { style: BorderStyle.SINGLE, size: 12, color: "333333" },
                      bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                    },
                  }),
                  new TableCell({
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun({
                            text: formatCAD(standardTier.total_price),
                            bold: true,
                          }),
                        ],
                        alignment: AlignmentType.RIGHT,
                      }),
                    ],
                    borders: {
                      top: { style: BorderStyle.SINGLE, size: 12, color: "333333" },
                      bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                      right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                    },
                  }),
                ],
              }),
            ],
          }),

          // Footer
          new Paragraph({
            children: [
              new TextRun({
                text:
                  locale === "fr"
                    ? "Cette soumission est valide pour 30 jours a compter de la date d'emission."
                    : "This quote is valid for 30 days from the date of issue.",
                size: 18, // 9pt in half-points
                color: "666666",
              }),
            ],
            spacing: { before: 400 },
            alignment: AlignmentType.CENTER,
          }),
        ],
      },
    ],
  });

  return await Packer.toBlob(doc);
}
