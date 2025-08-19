-- TEKNOFEST 2025 Adres Çözümleme Sistemi - Database Schema
-- PostgreSQL 15+ with PostGIS Extension
-- File: database/001_create_tables.sql

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main addresses table
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    raw_address TEXT NOT NULL,
    normalized_address TEXT,
    corrected_address TEXT,
    parsed_components JSONB,
    coordinates GEOMETRY(POINT, 4326),
    confidence_score DECIMAL(5,3),
    validation_status VARCHAR(20) CHECK (validation_status IN ('valid', 'invalid', 'needs_review')),
    processing_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add comments for better documentation
COMMENT ON TABLE addresses IS 'Main table storing address data with parsing and validation results';
COMMENT ON COLUMN addresses.raw_address IS 'Original unprocessed address string';
COMMENT ON COLUMN addresses.normalized_address IS 'Cleaned and normalized address';
COMMENT ON COLUMN addresses.corrected_address IS 'Address after spelling correction and abbreviation expansion';
COMMENT ON COLUMN addresses.parsed_components IS 'JSON object containing parsed address components (il, ilce, mahalle, sokak, etc.)';
COMMENT ON COLUMN addresses.coordinates IS 'PostGIS point geometry in WGS84 (SRID 4326)';
COMMENT ON COLUMN addresses.confidence_score IS 'Overall confidence score (0.000 to 1.000)';
COMMENT ON COLUMN addresses.validation_status IS 'Address validation status';
COMMENT ON COLUMN addresses.processing_metadata IS 'JSON metadata about processing steps and algorithms used';

-- Duplicate groups table
CREATE TABLE duplicate_groups (
    id SERIAL PRIMARY KEY,
    group_hash VARCHAR(64) UNIQUE,
    representative_address_id INTEGER REFERENCES addresses(id),
    member_count INTEGER DEFAULT 1,
    average_confidence DECIMAL(5,3),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add comments for duplicate_groups
COMMENT ON TABLE duplicate_groups IS 'Groups of duplicate addresses identified by the matching algorithm';
COMMENT ON COLUMN duplicate_groups.group_hash IS 'Unique hash identifying this duplicate group';
COMMENT ON COLUMN duplicate_groups.representative_address_id IS 'ID of the address chosen as representative for this group';
COMMENT ON COLUMN duplicate_groups.member_count IS 'Number of addresses in this duplicate group';
COMMENT ON COLUMN duplicate_groups.average_confidence IS 'Average confidence score of addresses in this group';

-- Duplicate relationships table  
CREATE TABLE duplicate_relationships (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES duplicate_groups(id),
    address_id INTEGER REFERENCES addresses(id),
    similarity_score DECIMAL(5,3),
    similarity_breakdown JSONB,
    UNIQUE(group_id, address_id)
);

-- Add comments for duplicate_relationships
COMMENT ON TABLE duplicate_relationships IS 'Many-to-many relationship between duplicate groups and addresses';
COMMENT ON COLUMN duplicate_relationships.similarity_score IS 'Overall similarity score for this address-group relationship';
COMMENT ON COLUMN duplicate_relationships.similarity_breakdown IS 'JSON breakdown of similarity scores (semantic, geographic, textual, hierarchical)';

-- Performance logs table
CREATE TABLE processing_logs (
    id SERIAL PRIMARY KEY,
    request_id UUID DEFAULT uuid_generate_v4(),
    operation_type VARCHAR(50),
    input_data JSONB,
    output_data JSONB,
    processing_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add comments for processing_logs
COMMENT ON TABLE processing_logs IS 'Audit log of all processing operations for performance monitoring';
COMMENT ON COLUMN processing_logs.request_id IS 'Unique identifier for tracking requests across operations';
COMMENT ON COLUMN processing_logs.operation_type IS 'Type of operation (process_address, batch_process, match_addresses, etc.)';
COMMENT ON COLUMN processing_logs.input_data IS 'JSON representation of input parameters';
COMMENT ON COLUMN processing_logs.output_data IS 'JSON representation of operation results';
COMMENT ON COLUMN processing_logs.processing_time_ms IS 'Processing time in milliseconds';
COMMENT ON COLUMN processing_logs.error_message IS 'Error message if operation failed';

-- Performance indexes
CREATE INDEX idx_addresses_normalized ON addresses (normalized_address);
CREATE INDEX idx_addresses_geom ON addresses USING GIST (coordinates);
CREATE INDEX idx_addresses_components ON addresses USING GIN (parsed_components);
CREATE INDEX idx_addresses_confidence ON addresses (confidence_score DESC);
CREATE INDEX idx_addresses_validation_status ON addresses (validation_status);
CREATE INDEX idx_addresses_created_at ON addresses (created_at DESC);

-- Indexes for duplicate_groups table
CREATE INDEX idx_duplicate_groups_hash ON duplicate_groups (group_hash);
CREATE INDEX idx_duplicate_groups_representative ON duplicate_groups (representative_address_id);
CREATE INDEX idx_duplicate_groups_member_count ON duplicate_groups (member_count DESC);

-- Indexes for duplicate_relationships table
CREATE INDEX idx_duplicate_relationships_group_id ON duplicate_relationships (group_id);
CREATE INDEX idx_duplicate_relationships_address_id ON duplicate_relationships (address_id);
CREATE INDEX idx_duplicate_relationships_similarity ON duplicate_relationships (similarity_score DESC);

-- Indexes for processing_logs table
CREATE INDEX idx_processing_logs_request ON processing_logs (request_id);
CREATE INDEX idx_processing_logs_operation ON processing_logs (operation_type);
CREATE INDEX idx_processing_logs_created_at ON processing_logs (created_at DESC);
CREATE INDEX idx_processing_logs_processing_time ON processing_logs (processing_time_ms DESC);

-- Additional specialized indexes for common queries

-- Composite indexes for better query performance
CREATE INDEX idx_addresses_status_confidence ON addresses (validation_status, confidence_score DESC);
CREATE INDEX idx_addresses_geom_confidence ON addresses USING GIST (coordinates) WHERE confidence_score > 0.7;

-- Partial indexes for better performance on filtered queries
CREATE INDEX idx_addresses_valid_only ON addresses (id) WHERE validation_status = 'valid';
CREATE INDEX idx_addresses_high_confidence ON addresses (id, confidence_score) WHERE confidence_score > 0.8;
CREATE INDEX idx_processing_logs_errors_only ON processing_logs (created_at DESC) WHERE error_message IS NOT NULL;

-- Function-based indexes for text searches
CREATE INDEX idx_addresses_raw_text_search ON addresses USING GIN (to_tsvector('turkish', raw_address));
CREATE INDEX idx_addresses_normalized_text_search ON addresses USING GIN (to_tsvector('turkish', normalized_address));

-- Add constraints for data integrity
ALTER TABLE addresses ADD CONSTRAINT chk_addresses_confidence_range 
    CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1));

ALTER TABLE duplicate_groups ADD CONSTRAINT chk_duplicate_groups_member_count_positive 
    CHECK (member_count > 0);

ALTER TABLE duplicate_groups ADD CONSTRAINT chk_duplicate_groups_confidence_range 
    CHECK (average_confidence IS NULL OR (average_confidence >= 0 AND average_confidence <= 1));

ALTER TABLE duplicate_relationships ADD CONSTRAINT chk_duplicate_relationships_similarity_range 
    CHECK (similarity_score IS NULL OR (similarity_score >= 0 AND similarity_score <= 1));

ALTER TABLE processing_logs ADD CONSTRAINT chk_processing_logs_time_positive 
    CHECK (processing_time_ms IS NULL OR processing_time_ms >= 0);

-- Add triggers for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_addresses_updated_at 
    BEFORE UPDATE ON addresses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions for application user (to be created separately)
-- These will be commented out for now and can be enabled when setting up the application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON addresses TO teknofest_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON duplicate_groups TO teknofest_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON duplicate_relationships TO teknofest_app_user;
-- GRANT SELECT, INSERT ON processing_logs TO teknofest_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO teknofest_app_user;