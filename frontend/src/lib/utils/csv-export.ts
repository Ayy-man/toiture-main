/**
 * CSV export utility with UTF-8 BOM for French character support.
 * Produces Excel-compatible CSV files.
 */

export function exportToCSV<T extends object>(
  data: T[],
  filename: string
): void {
  if (data.length === 0) return;

  const headers = Object.keys(data[0]) as (keyof T)[];
  const csvContent = [
    headers.join(","),
    ...data.map((row) =>
      headers
        .map((header) => {
          const value = row[header as keyof T];
          const str = String(value ?? "").replace(/"/g, '""');
          return str.includes(",") || str.includes('"') || str.includes("\n")
            ? `"${str}"`
            : str;
        })
        .join(",")
    ),
  ].join("\n");

  // UTF-8 BOM for Excel French character support
  const BOM = "\uFEFF";
  const blob = new Blob([BOM + csvContent], {
    type: "text/csv;charset=utf-8;",
  });

  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${filename}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
}
