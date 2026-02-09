-- Materials table for Laurent's 1,152-item inventory
-- Run this SQL manually in Supabase Dashboard SQL Editor before running import script

-- Enable pg_trgm extension for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create materials table
CREATE TABLE IF NOT EXISTS materials (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(100),  -- Supplier code from CODE column (nullable)
    name TEXT NOT NULL,
    cost DECIMAL(10,2),  -- 43 items missing
    sell_price DECIMAL(10,2),  -- 42 items missing
    unit VARCHAR(50) NOT NULL,
    category VARCHAR(100),  -- 231 items missing
    supplier VARCHAR(200),
    note TEXT,
    area_sqft DECIMAL(10,2) DEFAULT 0,
    length_ft DECIMAL(10,2) DEFAULT 0,
    width_ft DECIMAL(10,2) DEFAULT 0,
    thickness_ft DECIMAL(10,2) DEFAULT 0,
    item_type VARCHAR(20) DEFAULT 'material',  -- 'material' or 'labor'
    ml_material_id INTEGER,  -- For future ML model mapping (nullable)
    review_status VARCHAR(20) DEFAULT 'approved',  -- 'approved', 'flagged', 'duplicate'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_materials_category ON materials(category);
CREATE INDEX idx_materials_name_trgm ON materials USING gin(name gin_trgm_ops);
CREATE INDEX idx_materials_code ON materials(code) WHERE code IS NOT NULL;
CREATE INDEX idx_materials_review ON materials(review_status);
CREATE INDEX idx_materials_item_type ON materials(item_type);

-- Comments for documentation
COMMENT ON TABLE materials IS 'Laurent''s roofing materials inventory imported from LV Material List.csv';
COMMENT ON COLUMN materials.review_status IS 'approved = clean data, flagged = incomplete/labor, duplicate = near-duplicate detected';
COMMENT ON COLUMN materials.item_type IS 'material = physical item, labor = service/labor item';
COMMENT ON COLUMN materials.ml_material_id IS 'Links to ML model material IDs for future integration';
