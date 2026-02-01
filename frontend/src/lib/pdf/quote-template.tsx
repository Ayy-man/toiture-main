import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
} from "@react-pdf/renderer";
import type { HybridQuoteResponse, WorkItem, PricingTier } from "@/types/hybrid-quote";

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
}

// Format number as CAD currency (French Canadian format)
function formatCAD(amount: number): string {
  return new Intl.NumberFormat("fr-CA", {
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
}: QuotePDFDocumentProps) {
  // Get Standard tier for pricing
  const standardTier = quote.pricing_tiers.find(
    (tier) => tier.tier === "Standard"
  ) as PricingTier;

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>SOUMISSION</Text>
          <Text style={styles.subtitle}>Toiture LV</Text>
        </View>

        {/* Job Info */}
        <View style={styles.section}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Date:</Text>
            <Text style={styles.infoValue}>{date}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Categorie:</Text>
            <Text style={styles.infoValue}>{category}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Superficie:</Text>
            <Text style={styles.infoValue}>
              {sqft.toLocaleString("fr-CA")} pi2
            </Text>
          </View>
        </View>

        {/* Work Items - NO HOURS (client facing) */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Travaux</Text>
          {quote.work_items.map((item: WorkItem, index: number) => (
            <View key={index} style={styles.workItem}>
              <Text style={styles.bullet}>•</Text>
              <Text style={styles.itemText}>{item.name}</Text>
            </View>
          ))}
        </View>

        {/* Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Sommaire</Text>
          <View style={styles.summaryRow}>
            <Text>Materiaux</Text>
            <Text>{formatCAD(standardTier.materials_cost)}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text>Main-d&apos;oeuvre</Text>
            <Text>{formatCAD(standardTier.labor_cost)}</Text>
          </View>
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>TOTAL</Text>
            <Text style={styles.totalValue}>
              {formatCAD(standardTier.total_price)}
            </Text>
          </View>
        </View>

        {/* Footer */}
        <Text style={styles.footer}>
          Cette soumission est valide pour 30 jours a compter de la date
          d&apos;emission.
        </Text>
      </Page>
    </Document>
  );
}
