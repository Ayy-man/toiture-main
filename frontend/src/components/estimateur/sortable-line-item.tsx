"use client";

import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical, Trash2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/lib/i18n";
import type { LineItem } from "@/types/submission";

interface SortableLineItemProps {
  id: string;
  index: number;
  item: LineItem;
  onUpdate: (index: number, field: keyof LineItem, value: string | number) => void;
  onRemove: (index: number) => void;
  disabled: boolean;
}

export function SortableLineItem({
  id,
  index,
  item,
  onUpdate,
  onRemove,
  disabled,
}: SortableLineItemProps) {
  const { t } = useLanguage();
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  // Format total as CAD
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("fr-CA", {
      style: "currency",
      currency: "CAD",
    }).format(value);
  };

  const total = item.quantity * item.unit_price;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="flex gap-2 p-2 rounded-lg border bg-background items-center"
    >
      {/* Drag handle */}
      {!disabled && (
        <div
          {...attributes}
          {...listeners}
          className="cursor-grab active:cursor-grabbing"
        >
          <GripVertical className="h-5 w-5 text-muted-foreground" />
        </div>
      )}
      {disabled && <div className="w-5" />}

      {/* Type badge */}
      <Badge variant="outline" className="shrink-0 text-xs">
        {item.type === "material" ? t.submission.material : t.submission.labor}
      </Badge>

      {/* Name input */}
      <Input
        value={item.name}
        onChange={(e) => onUpdate(index, "name", e.target.value)}
        disabled={disabled}
        className="h-9 flex-1"
        placeholder={t.submission.lineItemName}
      />

      {/* Quantity input */}
      <Input
        type="number"
        min={0.01}
        step={0.01}
        value={item.quantity}
        onChange={(e) => onUpdate(index, "quantity", parseFloat(e.target.value) || 0)}
        disabled={disabled}
        className="h-9 w-20"
        placeholder="Qty"
      />

      {/* Unit price input */}
      <Input
        type="number"
        min={0}
        step={0.01}
        value={item.unit_price}
        onChange={(e) => onUpdate(index, "unit_price", parseFloat(e.target.value) || 0)}
        disabled={disabled}
        className="h-9 w-24"
        placeholder="Prix"
      />

      {/* Total display */}
      <span className="text-sm font-medium w-24 text-right tabular-nums">
        {formatCurrency(total)}
      </span>

      {/* Remove button */}
      {!disabled && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onRemove(index)}
          className="h-8 w-8 p-0"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      )}
      {disabled && <div className="w-8" />}
    </div>
  );
}
