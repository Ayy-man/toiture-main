"use client";

import { useLanguage } from "@/lib/i18n";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CATEGORIES } from "@/lib/schemas";
import type { QuoteFilters } from "@/types/quote";

interface QuoteFiltersProps {
  filters: QuoteFilters;
  onFiltersChange: (filters: QuoteFilters) => void;
  onExport: () => void;
  isExporting: boolean;
}

/**
 * Filter controls for the Historique quote browser.
 * Includes category, city, sqft range, price range, and date range filters.
 */
export function QuoteFiltersComponent({
  filters,
  onFiltersChange,
  onExport,
  isExporting,
}: QuoteFiltersProps) {
  const { t } = useLanguage();
  const updateFilter = <K extends keyof QuoteFilters>(
    key: K,
    value: QuoteFilters[K]
  ) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    onFiltersChange({});
  };

  return (
    <div className="space-y-4 mb-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium">{t.historique.filtres}</h2>
        <div className="flex gap-2">
          <Button variant="outline" onClick={clearFilters}>
            Effacer les filtres
          </Button>
          <Button onClick={onExport} disabled={isExporting}>
            {isExporting ? t.common.chargement : t.historique.exporter}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Category */}
        <div className="space-y-2">
          <Label htmlFor="category">{t.historique.categorie}</Label>
          <Select
            value={filters.category || "__all__"}
            onValueChange={(value) =>
              updateFilter("category", value === "__all__" ? undefined : value)
            }
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Toutes les catégories" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">Toutes les catégories</SelectItem>
              {CATEGORIES.map((cat) => (
                <SelectItem key={cat} value={cat}>
                  {cat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* City */}
        <div className="space-y-2">
          <Label htmlFor="city">{t.historique.ville}</Label>
          <Input
            id="city"
            placeholder="Rechercher une ville..."
            value={filters.city || ""}
            onChange={(e) => updateFilter("city", e.target.value || undefined)}
          />
        </div>

        {/* Sqft Min */}
        <div className="space-y-2">
          <Label htmlFor="min_sqft">Superficie min (pi2)</Label>
          <Input
            id="min_sqft"
            type="number"
            placeholder="0"
            value={filters.min_sqft || ""}
            onChange={(e) =>
              updateFilter(
                "min_sqft",
                e.target.value ? Number(e.target.value) : undefined
              )
            }
          />
        </div>

        {/* Sqft Max */}
        <div className="space-y-2">
          <Label htmlFor="max_sqft">Superficie max (pi2)</Label>
          <Input
            id="max_sqft"
            type="number"
            placeholder="100000"
            value={filters.max_sqft || ""}
            onChange={(e) =>
              updateFilter(
                "max_sqft",
                e.target.value ? Number(e.target.value) : undefined
              )
            }
          />
        </div>

        {/* Price Min */}
        <div className="space-y-2">
          <Label htmlFor="min_price">Prix min ($)</Label>
          <Input
            id="min_price"
            type="number"
            placeholder="0"
            value={filters.min_price || ""}
            onChange={(e) =>
              updateFilter(
                "min_price",
                e.target.value ? Number(e.target.value) : undefined
              )
            }
          />
        </div>

        {/* Price Max */}
        <div className="space-y-2">
          <Label htmlFor="max_price">Prix max ($)</Label>
          <Input
            id="max_price"
            type="number"
            placeholder="1000000"
            value={filters.max_price || ""}
            onChange={(e) =>
              updateFilter(
                "max_price",
                e.target.value ? Number(e.target.value) : undefined
              )
            }
          />
        </div>

        {/* Date Start */}
        <div className="space-y-2">
          <Label htmlFor="start_date">{t.historique.dateDebut}</Label>
          <Input
            id="start_date"
            type="date"
            value={filters.start_date || ""}
            onChange={(e) =>
              updateFilter("start_date", e.target.value || undefined)
            }
          />
        </div>

        {/* Date End */}
        <div className="space-y-2">
          <Label htmlFor="end_date">{t.historique.dateFin}</Label>
          <Input
            id="end_date"
            type="date"
            value={filters.end_date || ""}
            onChange={(e) =>
              updateFilter("end_date", e.target.value || undefined)
            }
          />
        </div>
      </div>
    </div>
  );
}
