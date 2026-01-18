import type { CustomerResult, CustomerDetail } from "@/types/customer";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function searchCustomers(
  query: string,
  limit: number = 10
): Promise<CustomerResult[]> {
  if (query.length < 2) return [];

  const params = new URLSearchParams({
    q: query,
    limit: String(limit),
  });

  const response = await fetch(`${API_URL}/customers/search?${params}`);
  if (!response.ok) {
    throw new Error("Failed to search customers");
  }
  return response.json();
}

export async function getCustomerDetail(
  customerId: string
): Promise<CustomerDetail> {
  const response = await fetch(`${API_URL}/customers/${customerId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch customer details");
  }
  return response.json();
}
