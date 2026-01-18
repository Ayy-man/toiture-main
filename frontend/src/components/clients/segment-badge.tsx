import { Badge } from "@/components/ui/badge";
import type { CustomerSegment } from "@/types/customer";

interface SegmentBadgeProps {
  segment: CustomerSegment;
}

export function SegmentBadge({ segment }: SegmentBadgeProps) {
  switch (segment) {
    case "VIP":
      return (
        <Badge className="bg-amber-500 text-white border-transparent hover:bg-amber-600">
          VIP
        </Badge>
      );
    case "Regular":
      return <Badge variant="secondary">Regular</Badge>;
    case "New":
      return <Badge variant="outline">New</Badge>;
  }
}
