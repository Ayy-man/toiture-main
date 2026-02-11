import { Skeleton } from "@/components/ui/skeleton";
import { Card } from "@/components/ui/card";

interface TableSkeletonProps {
  rows?: number;
  columns?: number;
}

/**
 * Reusable table skeleton loader.
 * Shows animated skeleton for table structure during loading states.
 */
export function TableSkeleton({ rows = 5, columns = 4 }: TableSkeletonProps) {
  return (
    <Card className="overflow-hidden">
      <div className="p-4 space-y-3">
        {/* Header row with shorter skeletons */}
        <div className="flex gap-4">
          {Array.from({ length: columns }).map((_, i) => (
            <Skeleton key={`header-${i}`} className="h-4 w-24" />
          ))}
        </div>

        {/* Body rows with varying widths for natural look */}
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={`row-${rowIndex}`} className="flex gap-4">
            {Array.from({ length: columns }).map((_, colIndex) => {
              // Vary widths for natural appearance
              const widths = ["w-32", "w-24", "w-40", "w-28", "w-36", "w-20"];
              const width = widths[(rowIndex + colIndex) % widths.length];
              return <Skeleton key={`cell-${rowIndex}-${colIndex}`} className={`h-4 ${width}`} />;
            })}
          </div>
        ))}
      </div>
    </Card>
  );
}
