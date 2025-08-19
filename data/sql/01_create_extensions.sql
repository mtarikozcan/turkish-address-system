-- TEKNOFEST 2025 Turkish Address Resolution System
-- Database Initialization Script 1: PostGIS Extensions
-- 
-- This script enables PostGIS and related extensions for spatial operations
-- on Turkish geographic data.

-- Enable PostGIS extension for spatial operations
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable PostGIS topology extension
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Enable PostGIS raster extension
CREATE EXTENSION IF NOT EXISTS postgis_raster;

-- Enable fuzzy string matching for address similarity
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

-- Enable trigram matching for text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable unaccent for Turkish character handling
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable performance monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Verify PostGIS installation
SELECT PostGIS_Version();

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'PostGIS extensions successfully initialized for TEKNOFEST 2025';
END $$;