"use client";

import { useState, useEffect, useDeferredValue } from "react";
import { Check, ChevronsUpDown, X, Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  searchMaterials,
  fetchMaterialCategories,
  type MaterialItem,
} from "@/lib/api/materials";
import { useLanguage } from "@/lib/i18n";

export interface SelectedMaterial {
  id: number;
  name: string;
  category: string | null;
  sell_price: number | null;
  unit: string;
  isCustom?: boolean;
}

interface MaterialSelectorProps {
  selectedMaterials: SelectedMaterial[];
  onSelectionChange: (materials: SelectedMaterial[]) => void;
}

export function MaterialSelector({
  selectedMaterials,
  onSelectionChange,
}: MaterialSelectorProps) {
  const { t } = useLanguage();
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const deferredSearchTerm = useDeferredValue(searchTerm);
  const [searchResults, setSearchResults] = useState<MaterialItem[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [loading, setLoading] = useState(false);
  const [showCustomDialog, setShowCustomDialog] = useState(false);
  const [customName, setCustomName] = useState("");
  const [customPrice, setCustomPrice] = useState("");
  const [customUnit, setCustomUnit] = useState("sqft");

  // Fetch categories on mount
  useEffect(() => {
    fetchMaterialCategories()
      .then((data) => setCategories(data.categories))
      .catch((err) => console.error("Failed to fetch categories:", err));
  }, []);

  // Search materials when deferred search term changes
  useEffect(() => {
    if (deferredSearchTerm.length < 2) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    searchMaterials(
      deferredSearchTerm,
      selectedCategory === "all" ? undefined : selectedCategory,
      50
    )
      .then((data) => setSearchResults(data.materials))
      .catch((err) => console.error("Failed to search materials:", err))
      .finally(() => setLoading(false));
  }, [deferredSearchTerm, selectedCategory]);

  const toggleMaterial = (material: MaterialItem) => {
    const isSelected = selectedMaterials.some((m) => m.id === material.id);

    if (isSelected) {
      onSelectionChange(selectedMaterials.filter((m) => m.id !== material.id));
    } else {
      const newMaterial: SelectedMaterial = {
        id: material.id,
        name: material.name,
        category: material.category,
        sell_price: material.sell_price,
        unit: material.unit,
      };
      onSelectionChange([...selectedMaterials, newMaterial]);
    }
  };

  const removeMaterial = (id: number) => {
    onSelectionChange(selectedMaterials.filter((m) => m.id !== id));
  };

  const addCustomMaterial = () => {
    if (!customName.trim()) return;

    const customMaterial: SelectedMaterial = {
      id: -Date.now(), // Negative temporary ID
      name: customName.trim(),
      category: "Custom",
      sell_price: customPrice ? parseFloat(customPrice) : null,
      unit: customUnit,
      isCustom: true,
    };

    onSelectionChange([...selectedMaterials, customMaterial]);
    setShowCustomDialog(false);
    setCustomName("");
    setCustomPrice("");
    setCustomUnit("sqft");
  };

  const formatCurrency = (value: number | null) => {
    if (value === null) return t.casSimilaires.na;
    return new Intl.NumberFormat("fr-CA", {
      style: "currency",
      currency: "CAD",
    }).format(value);
  };

  const totalEstimatedCost = selectedMaterials.reduce((sum, mat) => {
    return sum + (mat.sell_price || 0);
  }, 0);

  return (
    <div className="space-y-4">
      {/* Category filter */}
      <div className="space-y-2">
        <Label>{t.historique.categorie}</Label>
        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t.materialSelector.touteCategories}</SelectItem>
            {categories.map((cat) => (
              <SelectItem key={cat} value={cat}>
                {cat}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Material search combobox */}
      <div className="space-y-2">
        <Label>{t.materialSelector.selectionner}</Label>
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={open}
              className="w-full justify-between"
            >
              {selectedMaterials.length > 0
                ? `${selectedMaterials.length} ${t.materialSelector.materiauSelectionnes}`
                : t.materialSelector.selectionner}
              <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-[400px] p-0">
            <Command>
              <CommandInput
                placeholder={t.materialSelector.rechercher}
                value={searchTerm}
                onValueChange={setSearchTerm}
              />
              <CommandList className="max-h-64 overflow-auto">
                <CommandEmpty>
                  {loading
                    ? t.common.chargement
                    : t.materialSelector.aucunResultat}
                </CommandEmpty>
                <CommandGroup>
                  {searchResults.map((material) => {
                    const isSelected = selectedMaterials.some(
                      (m) => m.id === material.id
                    );
                    return (
                      <CommandItem
                        key={material.id}
                        value={material.name}
                        onSelect={() => toggleMaterial(material)}
                      >
                        <Check
                          className={cn(
                            "mr-2 h-4 w-4",
                            isSelected ? "opacity-100" : "opacity-0"
                          )}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium truncate">
                            {material.name}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {material.category} • {formatCurrency(material.sell_price)}
                          </div>
                        </div>
                      </CommandItem>
                    );
                  })}
                  {/* Add custom material button */}
                  {searchTerm.length >= 2 && (
                    <CommandItem
                      onSelect={() => {
                        setOpen(false);
                        setShowCustomDialog(true);
                      }}
                      className="border-t"
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      {t.materialSelector.ajouterPersonnalise}
                    </CommandItem>
                  )}
                </CommandGroup>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      </div>

      {/* Selected materials list */}
      {selectedMaterials.length > 0 && (
        <div className="rounded-lg border p-4 space-y-3">
          <div className="text-sm font-medium">
            {selectedMaterials.length} {t.materialSelector.materiauSelectionnes}
          </div>
          <div className="space-y-2">
            {selectedMaterials.map((material) => (
              <div
                key={material.id}
                className="flex items-center justify-between gap-2 rounded-md bg-muted/50 p-2"
              >
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate">
                    {material.name}
                    {material.isCustom && (
                      <span className="ml-2 text-xs text-muted-foreground">
                        (Custom)
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {material.category} • {formatCurrency(material.sell_price)} / {material.unit}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeMaterial(material.id)}
                  className="h-8 w-8 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
          {/* Total cost */}
          <div className="flex justify-between items-center pt-2 border-t text-sm font-medium">
            <span>{t.materiaux.coutTotal}:</span>
            <span>{formatCurrency(totalEstimatedCost)}</span>
          </div>
        </div>
      )}

      {/* Custom material dialog */}
      <Dialog open={showCustomDialog} onOpenChange={setShowCustomDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t.materialSelector.ajouterPersonnalise}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="custom-name">
                {t.materialSelector.nomPersonnalise}
              </Label>
              <Input
                id="custom-name"
                value={customName}
                onChange={(e) => setCustomName(e.target.value)}
                placeholder={t.materialSelector.nomPersonnalise}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="custom-price">
                {t.materialSelector.prixPersonnalise}
              </Label>
              <Input
                id="custom-price"
                type="number"
                step="0.01"
                value={customPrice}
                onChange={(e) => setCustomPrice(e.target.value)}
                placeholder="0.00"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="custom-unit">
                {t.materialSelector.unitePersonnalisee}
              </Label>
              <Input
                id="custom-unit"
                value={customUnit}
                onChange={(e) => setCustomUnit(e.target.value)}
                placeholder="sqft"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowCustomDialog(false)}
            >
              {t.materialSelector.annuler}
            </Button>
            <Button onClick={addCustomMaterial} disabled={!customName.trim()}>
              {t.materialSelector.ajouter}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
