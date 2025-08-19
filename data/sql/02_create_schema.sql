-- TEKNOFEST 2025 Turkish Address Resolution System
-- Database Initialization Script 2: Schema Creation
-- 
-- This script creates the complete database schema for Turkish address resolution
-- with PostGIS spatial support and optimized indexes.

-- Create main addresses table with spatial support
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    
    -- Address text fields
    raw_address TEXT NOT NULL,
    normalized_address TEXT,
    corrected_address TEXT,
    
    -- Parsed components as JSONB
    parsed_components JSONB DEFAULT '{}',
    
    -- Spatial data with WGS84 (SRID 4326)
    coordinates GEOMETRY(POINT, 4326),
    
    -- Validation and confidence
    confidence_score FLOAT DEFAULT 0.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    validation_status VARCHAR(20) DEFAULT 'needs_review' CHECK (validation_status IN ('valid', 'invalid', 'needs_review')),
    
    -- Processing metadata
    processing_metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_addresses_coordinates 
    ON addresses USING GIST (coordinates);

CREATE INDEX IF NOT EXISTS idx_addresses_components 
    ON addresses USING GIN (parsed_components);

CREATE INDEX IF NOT EXISTS idx_addresses_normalized 
    ON addresses USING GIN (normalized_address gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_addresses_status 
    ON addresses (validation_status);

CREATE INDEX IF NOT EXISTS idx_addresses_confidence 
    ON addresses (confidence_score DESC);

-- Create indexes for Turkish administrative hierarchy
CREATE INDEX IF NOT EXISTS idx_addresses_il 
    ON addresses ((parsed_components->>'il'));

CREATE INDEX IF NOT EXISTS idx_addresses_ilce 
    ON addresses ((parsed_components->>'ilce'));

CREATE INDEX IF NOT EXISTS idx_addresses_mahalle 
    ON addresses ((parsed_components->>'mahalle'));

-- Create Turkish administrative hierarchy table
CREATE TABLE IF NOT EXISTS administrative_hierarchy (
    id SERIAL PRIMARY KEY,
    il VARCHAR(100) NOT NULL,
    ilce VARCHAR(100) NOT NULL,
    mahalle VARCHAR(100),
    postal_code VARCHAR(10),
    
    -- Spatial bounds for the administrative area
    bounds GEOMETRY(POLYGON, 4326),
    
    -- Metadata
    population INTEGER,
    area_km2 FLOAT,
    
    UNIQUE(il, ilce, mahalle)
);

CREATE INDEX IF NOT EXISTS idx_admin_hierarchy_il 
    ON administrative_hierarchy (il);

CREATE INDEX IF NOT EXISTS idx_admin_hierarchy_ilce 
    ON administrative_hierarchy (ilce);

CREATE INDEX IF NOT EXISTS idx_admin_hierarchy_bounds 
    ON administrative_hierarchy USING GIST (bounds);

-- Create abbreviations table for Turkish address corrections
CREATE TABLE IF NOT EXISTS turkish_abbreviations (
    id SERIAL PRIMARY KEY,
    abbreviation VARCHAR(50) NOT NULL UNIQUE,
    full_form VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    usage_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_abbreviations_abbrev 
    ON turkish_abbreviations (abbreviation);

-- Create common errors table for address corrections
CREATE TABLE IF NOT EXISTS turkish_common_errors (
    id SERIAL PRIMARY KEY,
    error_pattern VARCHAR(200) NOT NULL UNIQUE,
    correct_form VARCHAR(200) NOT NULL,
    error_type VARCHAR(50),
    correction_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_common_errors_pattern 
    ON turkish_common_errors (error_pattern);

-- Create POI (Points of Interest) table for Turkish landmarks
CREATE TABLE IF NOT EXISTS turkish_pois (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    il VARCHAR(100),
    ilce VARCHAR(100),
    address TEXT,
    coordinates GEOMETRY(POINT, 4326),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_pois_coordinates 
    ON turkish_pois USING GIST (coordinates);

CREATE INDEX IF NOT EXISTS idx_pois_name 
    ON turkish_pois USING GIN (name gin_trgm_ops);

-- Create processing logs table for monitoring
CREATE TABLE IF NOT EXISTS processing_logs (
    id SERIAL PRIMARY KEY,
    request_id UUID DEFAULT uuid_generate_v4(),
    address_id INTEGER REFERENCES addresses(id),
    processing_step VARCHAR(50),
    success BOOLEAN DEFAULT true,
    duration_ms FLOAT,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_logs_request_id 
    ON processing_logs (request_id);

CREATE INDEX IF NOT EXISTS idx_logs_created_at 
    ON processing_logs (created_at DESC);

-- Create update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_addresses_updated_at 
    BEFORE UPDATE ON addresses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function for finding nearby addresses
CREATE OR REPLACE FUNCTION find_nearby_addresses(
    lat FLOAT,
    lon FLOAT,
    radius_meters INTEGER DEFAULT 500,
    max_results INTEGER DEFAULT 20
)
RETURNS TABLE (
    id INTEGER,
    raw_address TEXT,
    distance_meters FLOAT,
    confidence_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.raw_address,
        ST_Distance(
            a.coordinates::geography,
            ST_SetSRID(ST_Point(lon, lat), 4326)::geography
        ) as distance_meters,
        a.confidence_score
    FROM addresses a
    WHERE ST_DWithin(
        a.coordinates::geography,
        ST_SetSRID(ST_Point(lon, lat), 4326)::geography,
        radius_meters
    )
    ORDER BY distance_meters ASC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Log successful schema creation
DO $$
BEGIN
    RAISE NOTICE 'Database schema successfully created for TEKNOFEST 2025';
END $$;