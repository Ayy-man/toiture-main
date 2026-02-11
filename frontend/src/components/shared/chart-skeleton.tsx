import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

/**
 * Reusable chart skeleton loader.
 * Shows animated skeleton for chart structure with bar-chart-like shapes.
 */
export function ChartSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-5 w-32" />
      </CardHeader>
      <CardContent>
        <div className="h-[200px] flex items-end gap-2 justify-around p-4">
          {/* Bar-chart-like skeleton shapes with varying heights */}
          <Skeleton className="h-32 w-12" />
          <Skeleton className="h-24 w-12" />
          <Skeleton className="h-40 w-12" />
          <Skeleton className="h-28 w-12" />
          <Skeleton className="h-36 w-12" />
          <Skeleton className="h-20 w-12" />
          <Skeleton className="h-32 w-12" />
        </div>
      </CardContent>
    </Card>
  );
}
