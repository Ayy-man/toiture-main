// Material types matching backend MaterialItem schema
export interface MaterialItem {
  id: number;
  code: string | null;
  name: string;
  cost: number | null;
  sell_price: number | null;
  unit: string;
  category: string | null;
  supplier: string | null;
  note: string | null;
  area_sqft: number;
  length_ft: number;
  width_ft: number;
  thickness_ft: number;
  item_type: string;
  ml_material_id: number | null;
  review_status: string;
}

export interface MaterialSearchResponse {
  materials: MaterialItem[];
  count: number;
  total_available: number;
}

export interface MaterialCategoryResponse {
  categories: string[];
  count: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function searchMaterials(
  q: string,
  category?: string,
  limit: number = 50
): Promise<MaterialSearchResponse> {
  if (q.length < 2) {
    return { materials: [], count: 0, total_available: 0 };
  }

  const params = new URLSearchParams({
    q,
    limit: String(limit),
  });

  if (category && category !== "all") {
    params.set("category", category);
  }

  const response = await fetch(`${API_URL}/materials/search?${params}`);
  if (!response.ok) {
    throw new Error("Failed to search materials");
  }
  return response.json();
}

export async function fetchMaterialCategories(): Promise<MaterialCategoryResponse> {
  const response = await fetch(`${API_URL}/materials/categories`);
  if (!response.ok) {
    throw new Error("Failed to fetch material categories");
  }
  return response.json();
}
