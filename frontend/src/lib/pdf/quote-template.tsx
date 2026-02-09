import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
} from "@react-pdf/renderer";
import type { HybridQuoteResponse, WorkItem, PricingTier } from "@/types/hybrid-quote";
import { fr } from "@/lib/i18n/fr";
import { en } from "@/lib/i18n/en";

const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontFamily: "Helvetica",
    fontSize: 11,
  },
  header: {
    marginBottom: 30,
    textAlign: "center",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 12,
    color: "#666",
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: "bold",
    borderBottomWidth: 1,
    borderBottomColor: "#333",
    paddingBottom: 4,
    marginBottom: 10,
    textTransform: "uppercase",
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 4,
  },
  workItem: {
    flexDirection: "row",
    paddingVertical: 3,
  },
  bullet: {
    width: 15,
  },
  itemText: {
    flex: 1,
  },
  summaryRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 6,
  },
  totalRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 10,
    borderTopWidth: 2,
    borderTopColor: "#333",
    marginTop: 10,
  },
  totalLabel: {
    fontSize: 14,
    fontWeight: "bold",
  },
  totalValue: {
    fontSize: 14,
    fontWeight: "bold",
  },
  footer: {
    position: "absolute",
    bottom: 30,
    left: 40,
    right: 40,
    textAlign: "center",
    fontSize: 9,
    color: "#666",
  },
  infoRow: {
    flexDirection: "row",
    marginBottom: 4,
  },
  infoLabel: {
    width: 100,
    fontWeight: "bold",
  },
  infoValue: {
    flex: 1,
  },
});

interface QuotePDFDocumentProps {
  quote: HybridQuoteResponse;
  category: string;
  sqft: number;
  date: string;
  locale?: string; // "fr" | "en", defaults to "fr"
}

// Format number as CAD currency (locale-aware format)
function formatCAD(amount: number, locale: string = "fr"): string {
  return new Intl.NumberFormat(locale === "en" ? "en-CA" : "fr-CA", {
    style: "currency",
    currency: "CAD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function QuotePDFDocument({
  quote,
  category,
  sqft,
  date,
  locale = "fr",
}: QuotePDFDocumentProps) {
  // Select translation set based on locale
  const t = locale === "en" ? en : fr;

  // Get Standard tier for pricing
  const standardTier = quote.pricing_tiers.find(
    (tier) => tier.tier === "Standard"
  ) as PricingTier;

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>{t.pdf.title}</Text>
          <Text style={styles.subtitle}>{t.pdf.company}</Text>
        </View>

        {/* Job Info */}
        <View style={styles.section}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>{t.pdf.dateLabel}</Text>
            <Text style={styles.infoValue}>{date}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>{t.pdf.categoryLabel}</Text>
            <Text style={styles.infoValue}>{category}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>{t.pdf.areaLabel}</Text>
            <Text style={styles.infoValue}>
              {sqft.toLocaleString(locale === "en" ? "en-CA" : "fr-CA")} {t.pdf.areaUnit}
            </Text>
          </View>
        </View>

        {/* Work Items - NO HOURS (client facing) */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t.pdf.workItemsTitle}</Text>
          {quote.work_items.map((item: WorkItem, index: number) => (
            <View key={index} style={styles.workItem}>
              <Text style={styles.bullet}>•</Text>
              <Text style={styles.itemText}>{item.name}</Text>
            </View>
          ))}
        </View>

        {/* Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t.pdf.summaryTitle}</Text>
          <View style={styles.summaryRow}>
            <Text>{t.pdf.materials}</Text>
            <Text>{formatCAD(standardTier.materials_cost, locale)}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text>{t.pdf.labor}</Text>
            <Text>{formatCAD(standardTier.labor_cost, locale)}</Text>
          </View>
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>{t.pdf.total}</Text>
            <Text style={styles.totalValue}>
              {formatCAD(standardTier.total_price, locale)}
            </Text>
          </View>
        </View>

        {/* Footer */}
        <Text style={styles.footer}>
          {t.pdf.footer}
        </Text>
      </Page>
    </Document>
  );
}
