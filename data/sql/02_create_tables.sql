-- TEKNOFEST 2025 Turkish Address Resolution System
-- Database Initialization Script 2: Table Creation
-- 
-- This script creates the main addresses table and related structures
-- for storing Turkish address data with spatial indexing.

-- Main addresses table for Turkish address data
CREATE TABLE IF NOT EXISTS addresses (
    -- Primary key
    id SERIAL PRIMARY KEY,
    
    -- Address data fields
    raw_address TEXT NOT NULL,
    normalized_address TEXT,
    corrected_address TEXT,
    
    -- JSONB fields for structured data
    parsed_components JSONB NOT NULL DEFAULT '{}',
    processing_metadata JSONB DEFAULT '{}',
    
    -- Spatial data (WGS84 - EPSG:4326)
    coordinates GEOMETRY(POINT, 4326),
    
    -- Quality metrics
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    validation_status VARCHAR(20) DEFAULT 'needs_review' 
        CHECK (validation_status IN ('valid', 'invalid', 'needs_review')),
    
    -- Performance tracking
    processing_time_ms FLOAT,
    algorithm_versions JSONB DEFAULT '{}',
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Search optimization
    search_vector tsvector
);

-- Turkish administrative hierarchy table
CREATE TABLE IF NOT EXISTS turkish_admin_hierarchy (
    id SERIAL PRIMARY KEY,
    
    -- Administrative levels
    il_code VARCHAR(2) NOT NULL,
    il_name VARCHAR(50) NOT NULL,
    ilce_code VARCHAR(4),
    ilce_name VARCHAR(100),
    mahalle_code VARCHAR(10),
    mahalle_name VARCHAR(200),
    
    -- Geographic data
    bounds GEOMETRY(POLYGON, 4326),
    center_point GEOMETRY(POINT, 4326),
    
    -- Metadata
    population INTEGER,
    area_km2 FLOAT,
    postal_codes TEXT[],
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Address processing log table for monitoring
CREATE TABLE IF NOT EXISTS address_processing_log (
    id SERIAL PRIMARY KEY,
    
    -- Request tracking
    request_id UUID DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100),
    
    -- Input data
    raw_address TEXT NOT NULL,
    processing_type VARCHAR(50) DEFAULT 'standard',
    
    -- Processing results
    status VARCHAR(20) NOT NULL DEFAULT 'processing'
        CHECK (status IN ('processing', 'completed', 'error', 'timeout')),
    
    -- Performance metrics
    total_processing_time_ms FLOAT,
    step_times JSONB DEFAULT '{}',
    
    -- Results
    final_confidence FLOAT,
    matches_found INTEGER DEFAULT 0,
    
    -- Error handling
    error_message TEXT,
    error_code VARCHAR(50),
    
    -- System info
    algorithm_versions JSONB DEFAULT '{}',
    system_load JSONB DEFAULT '{}',
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexing
    CONSTRAINT valid_confidence CHECK (final_confidence IS NULL OR (final_confidence >= 0 AND final_confidence <= 1))
);

-- Performance benchmarks table
CREATE TABLE IF NOT EXISTS performance_benchmarks (
    id SERIAL PRIMARY KEY,
    
    -- Test configuration
    test_name VARCHAR(100) NOT NULL,
    test_category VARCHAR(50) NOT NULL,
    test_date DATE DEFAULT CURRENT_DATE,
    
    -- Performance metrics
    addresses_processed INTEGER NOT NULL,
    total_time_seconds FLOAT NOT NULL,
    avg_time_per_address_ms FLOAT NOT NULL,
    throughput_per_second FLOAT NOT NULL,
    
    -- Quality metrics
    success_rate FLOAT NOT NULL,
    avg_confidence FLOAT,
    
    -- System configuration
    database_version VARCHAR(50),
    postgis_version VARCHAR(50),
    system_config JSONB DEFAULT '{}',
    
    -- Results
    test_results JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for optimal performance

-- Primary spatial index on coordinates
CREATE INDEX IF NOT EXISTS idx_addresses_coordinates 
ON addresses USING GIST (coordinates);

-- JSONB indexes for component searching
CREATE INDEX IF NOT EXISTS idx_addresses_parsed_components 
ON addresses USING GIN (parsed_components);

CREATE INDEX IF NOT EXISTS idx_addresses_processing_metadata 
ON addresses USING GIN (processing_metadata);

-- Text search indexes
CREATE INDEX IF NOT EXISTS idx_addresses_raw_address_trgm 
ON addresses USING GIN (raw_address gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_addresses_corrected_address_trgm 
ON addresses USING GIN (corrected_address gin_trgm_ops);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_addresses_search_vector 
ON addresses USING GIN (search_vector);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_addresses_confidence_score 
ON addresses (confidence_score DESC);

CREATE INDEX IF NOT EXISTS idx_addresses_validation_status 
ON addresses (validation_status);

CREATE INDEX IF NOT EXISTS idx_addresses_created_at 
ON addresses (created_at DESC);

-- Administrative hierarchy indexes
CREATE INDEX IF NOT EXISTS idx_turkish_admin_hierarchy_il 
ON turkish_admin_hierarchy (il_name);

CREATE INDEX IF NOT EXISTS idx_turkish_admin_hierarchy_ilce 
ON turkish_admin_hierarchy (il_name, ilce_name);

CREATE INDEX IF NOT EXISTS idx_turkish_admin_hierarchy_mahalle 
ON turkish_admin_hierarchy (il_name, ilce_name, mahalle_name);

CREATE INDEX IF NOT EXISTS idx_turkish_admin_hierarchy_bounds 
ON turkish_admin_hierarchy USING GIST (bounds);

CREATE INDEX IF NOT EXISTS idx_turkish_admin_hierarchy_center 
ON turkish_admin_hierarchy USING GIST (center_point);

-- Processing log indexes
CREATE INDEX IF NOT EXISTS idx_processing_log_request_id 
ON address_processing_log (request_id);

CREATE INDEX IF NOT EXISTS idx_processing_log_status 
ON address_processing_log (status);

CREATE INDEX IF NOT EXISTS idx_processing_log_started_at 
ON address_processing_log (started_at DESC);

CREATE INDEX IF NOT EXISTS idx_processing_log_performance 
ON address_processing_log (total_processing_time_ms, final_confidence);

-- Benchmark indexes
CREATE INDEX IF NOT EXISTS idx_benchmarks_test_name_date 
ON performance_benchmarks (test_name, test_date DESC);

-- Create triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_addresses_updated_at 
    BEFORE UPDATE ON addresses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hierarchy_updated_at 
    BEFORE UPDATE ON turkish_admin_hierarchy 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function for updating search vectors
CREATE OR REPLACE FUNCTION update_address_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('turkish', COALESCE(NEW.raw_address, '')), 'A') ||
        setweight(to_tsvector('turkish', COALESCE(NEW.corrected_address, '')), 'B') ||
        setweight(to_tsvector('turkish', COALESCE(NEW.parsed_components->>'il', '')), 'C') ||
        setweight(to_tsvector('turkish', COALESCE(NEW.parsed_components->>'ilce', '')), 'C') ||
        setweight(to_tsvector('turkish', COALESCE(NEW.parsed_components->>'mahalle', '')), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply search vector trigger
CREATE TRIGGER update_address_search_vector_trigger
    BEFORE INSERT OR UPDATE ON addresses
    FOR EACH ROW EXECUTE FUNCTION update_address_search_vector();

-- Create partitioning for performance (by date)
-- This helps with large datasets over time
CREATE TABLE IF NOT EXISTS address_processing_log_2025 
PARTITION OF address_processing_log
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Log successful table creation
DO $$
BEGIN
    RAISE NOTICE 'Database tables successfully created for TEKNOFEST 2025';
    RAISE NOTICE 'Tables: addresses, turkish_admin_hierarchy, address_processing_log, performance_benchmarks';
    RAISE NOTICE 'Indexes: spatial, JSONB, text search, and performance indexes created';
    RAISE NOTICE 'Triggers: automatic timestamp updates and search vector maintenance';
END $$;