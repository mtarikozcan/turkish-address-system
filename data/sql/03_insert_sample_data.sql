-- TEKNOFEST 2025 Turkish Address Resolution System
-- Database Initialization Script 3: Sample Turkish Data
-- 
-- This script inserts sample Turkish address data for integration testing
-- with real geographic coordinates and administrative hierarchy.

-- Insert Turkish administrative hierarchy data
INSERT INTO turkish_admin_hierarchy (
    il_code, il_name, ilce_code, ilce_name, mahalle_code, mahalle_name,
    center_point, population, area_km2, postal_codes
) VALUES
-- İstanbul data
('34', 'İstanbul', '3434', 'Kadıköy', '343401', 'Moda Mahallesi', 
 ST_SetSRID(ST_Point(29.0376, 40.9875), 4326), 45000, 2.5, ARRAY['34710', '34718']),

('34', 'İstanbul', '3434', 'Kadıköy', '343402', 'Caferağa Mahallesi', 
 ST_SetSRID(ST_Point(29.0356, 40.9845), 4326), 35000, 1.8, ARRAY['34710']),

('34', 'İstanbul', '3427', 'Beşiktaş', '342701', 'Levent Mahallesi', 
 ST_SetSRID(ST_Point(29.0103, 41.0789), 4326), 55000, 3.2, ARRAY['34330', '34394']),

-- Ankara data
('06', 'Ankara', '0625', 'Çankaya', '062501', 'Kızılay Mahallesi', 
 ST_SetSRID(ST_Point(32.8541, 39.9208), 4326), 25000, 1.2, ARRAY['06420', '06430']),

('06', 'Ankara', '0631', 'Yenimahalle', '063101', 'Batıkent Mahallesi', 
 ST_SetSRID(ST_Point(32.7356, 39.9756), 4326), 85000, 8.5, ARRAY['06370']),

-- İzmir data
('35', 'İzmir', '3520', 'Konak', '352001', 'Alsancak Mahallesi', 
 ST_SetSRID(ST_Point(27.1284, 38.4189), 4326), 32000, 2.1, ARRAY['35220']),

('35', 'İzmir', '3526', 'Bornova', '352601', 'Erzene Mahallesi', 
 ST_SetSRID(ST_Point(27.2156, 38.4531), 4326), 45000, 5.2, ARRAY['35040']),

-- Bursa data
('16', 'Bursa', '1625', 'Osmangazi', '162501', 'Soğanlı Mahallesi', 
 ST_SetSRID(ST_Point(29.0610, 40.1885), 4326), 28000, 3.1, ARRAY['16100']),

-- Antalya data
('07', 'Antalya', '0712', 'Muratpaşa', '071201', 'Lara Mahallesi', 
 ST_SetSRID(ST_Point(30.7925, 36.8333), 4326), 65000, 12.3, ARRAY['07100']),

-- Gaziantep data
('27', 'Gaziantep', '2730', 'Şahinbey', '273001', 'Güllüoğlu Mahallesi', 
 ST_SetSRID(ST_Point(37.3833, 37.0662), 4326), 42000, 4.7, ARRAY['27010']);

-- Insert sample address data for testing
INSERT INTO addresses (
    raw_address, normalized_address, corrected_address, parsed_components,
    coordinates, confidence_score, validation_status, processing_metadata
) VALUES
-- İstanbul addresses
('İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10', 
 'istanbul kadıköy moda mahallesi caferağa sokak no 10',
 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
 '{"il": "İstanbul", "ilce": "Kadıköy", "mahalle": "Moda Mahallesi", "sokak": "Caferağa Sokak", "bina_no": "10"}',
 ST_SetSRID(ST_Point(29.0376, 40.9875), 4326), 0.95, 'valid',
 '{"test_data": true, "category": "residential", "source": "sample"}'),

('İstanbul Beşiktaş Levent Mahallesi Kanyon AVM',
 'istanbul beşiktaş levent mahallesi kanyon avm',
 'İstanbul Beşiktaş Levent Mahallesi Kanyon Alışveriş Merkezi',
 '{"il": "İstanbul", "ilce": "Beşiktaş", "mahalle": "Levent Mahallesi", "poi": "Kanyon AVM"}',
 ST_SetSRID(ST_Point(29.0103, 41.0789), 4326), 0.92, 'valid',
 '{"test_data": true, "category": "commercial", "source": "sample"}'),

-- Ankara addresses
('Ankara Çankaya Kızılay Mahallesi Atatürk Bulvarı 25',
 'ankara çankaya kızılay mahallesi atatürk bulvarı 25',
 'Ankara Çankaya Kızılay Mahallesi Atatürk Bulvarı 25',
 '{"il": "Ankara", "ilce": "Çankaya", "mahalle": "Kızılay Mahallesi", "cadde": "Atatürk Bulvarı", "bina_no": "25"}',
 ST_SetSRID(ST_Point(32.8541, 39.9208), 4326), 0.88, 'valid',
 '{"test_data": true, "category": "commercial", "source": "sample"}'),

('Ankara Yenimahalle Batıkent Mahallesi 3. Etap',
 'ankara yenimahalle batıkent mahallesi 3. etap',
 'Ankara Yenimahalle Batıkent Mahallesi 3. Etap',
 '{"il": "Ankara", "ilce": "Yenimahalle", "mahalle": "Batıkent Mahallesi", "site": "3. Etap"}',
 ST_SetSRID(ST_Point(32.7356, 39.9756), 4326), 0.85, 'valid',
 '{"test_data": true, "category": "residential", "source": "sample"}'),

-- İzmir addresses
('İzmir Konak Alsancak Mahallesi Cumhuriyet Bulvarı 45',
 'izmir konak alsancak mahallesi cumhuriyet bulvarı 45',
 'İzmir Konak Alsancak Mahallesi Cumhuriyet Bulvarı 45',
 '{"il": "İzmir", "ilce": "Konak", "mahalle": "Alsancak Mahallesi", "cadde": "Cumhuriyet Bulvarı", "bina_no": "45"}',
 ST_SetSRID(ST_Point(27.1284, 38.4189), 4326), 0.91, 'valid',
 '{"test_data": true, "category": "commercial", "source": "sample"}'),

('İzmir Bornova Erzene Mahallesi Bornova Caddesi',
 'izmir bornova erzene mahallesi bornova caddesi',
 'İzmir Bornova Erzene Mahallesi Bornova Caddesi',
 '{"il": "İzmir", "ilce": "Bornova", "mahalle": "Erzene Mahallesi", "cadde": "Bornova Caddesi"}',
 ST_SetSRID(ST_Point(27.2156, 38.4531), 4326), 0.83, 'valid',
 '{"test_data": true, "category": "mixed", "source": "sample"}'),

-- Bursa addresses
('Bursa Osmangazi Soğanlı Mahallesi',
 'bursa osmangazi soğanlı mahallesi',
 'Bursa Osmangazi Soğanlı Mahallesi',
 '{"il": "Bursa", "ilce": "Osmangazi", "mahalle": "Soğanlı Mahallesi"}',
 ST_SetSRID(ST_Point(29.0610, 40.1885), 4326), 0.78, 'valid',
 '{"test_data": true, "category": "incomplete", "source": "sample"}'),

-- Antalya addresses
('Antalya Muratpaşa Lara Plajı Kumsal Sokak',
 'antalya muratpaşa lara plajı kumsal sokak',
 'Antalya Muratpaşa Lara Mahallesi Kumsal Sokak',
 '{"il": "Antalya", "ilce": "Muratpaşa", "mahalle": "Lara Mahallesi", "sokak": "Kumsal Sokak", "poi": "Lara Plajı"}',
 ST_SetSRID(ST_Point(30.7925, 36.8333), 4326), 0.86, 'valid',
 '{"test_data": true, "category": "tourism", "source": "sample"}'),

-- Gaziantep addresses
('Gaziantep Şahinbey Güllüoğlu Baklava Fabrikası',
 'gaziantep şahinbey güllüoğlu baklava fabrikası',
 'Gaziantep Şahinbey Güllüoğlu Mahallesi Baklava Fabrikası',
 '{"il": "Gaziantep", "ilce": "Şahinbey", "mahalle": "Güllüoğlu Mahallesi", "poi": "Baklava Fabrikası"}',
 ST_SetSRID(ST_Point(37.3833, 37.0662), 4326), 0.89, 'valid',
 '{"test_data": true, "category": "business", "source": "sample"}'),

-- Test addresses with corrections needed
('istanbul kadikoy moda mah caferaga sk 10',
 'istanbul kadikoy moda mah caferaga sk 10',
 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
 '{"il": "İstanbul", "ilce": "Kadıköy", "mahalle": "Moda Mahallesi", "sokak": "Caferağa Sokak", "bina_no": "10"}',
 ST_SetSRID(ST_Point(29.0376, 40.9875), 4326), 0.87, 'valid',
 '{"test_data": true, "category": "needs_correction", "source": "sample", "corrections_applied": ["case", "abbreviations"]}'),

-- Addresses for performance testing
('Test Performance Address 1 İstanbul Kadıköy',
 'test performance address 1 istanbul kadıköy',
 'Test Performance Address 1 İstanbul Kadıköy',
 '{"il": "İstanbul", "ilce": "Kadıköy", "test": true}',
 ST_SetSRID(ST_Point(29.0300, 40.9800), 4326), 0.75, 'needs_review',
 '{"test_data": true, "category": "performance", "source": "sample"}'),

('Test Performance Address 2 Ankara Çankaya',
 'test performance address 2 ankara çankaya',
 'Test Performance Address 2 Ankara Çankaya',
 '{"il": "Ankara", "ilce": "Çankaya", "test": true}',
 ST_SetSRID(ST_Point(32.8500, 39.9200), 4326), 0.72, 'needs_review',
 '{"test_data": true, "category": "performance", "source": "sample"}');

-- Insert sample processing log entries
INSERT INTO address_processing_log (
    request_id, raw_address, status, total_processing_time_ms, 
    final_confidence, matches_found, algorithm_versions
) VALUES
(uuid_generate_v4(), 'İstanbul Kadıköy Test Log 1', 'completed', 45.2, 0.89, 3,
 '{"corrector": "1.0", "parser": "1.0", "validator": "1.0", "matcher": "1.0"}'),

(uuid_generate_v4(), 'Ankara Çankaya Test Log 2', 'completed', 52.8, 0.92, 5,
 '{"corrector": "1.0", "parser": "1.0", "validator": "1.0", "matcher": "1.0"}'),

(uuid_generate_v4(), 'İzmir Konak Test Log 3', 'completed', 38.7, 0.85, 2,
 '{"corrector": "1.0", "parser": "1.0", "validator": "1.0", "matcher": "1.0"}');

-- Insert sample performance benchmarks
INSERT INTO performance_benchmarks (
    test_name, test_category, addresses_processed, total_time_seconds,
    avg_time_per_address_ms, throughput_per_second, success_rate, avg_confidence,
    database_version, postgis_version, system_config
) VALUES
('baseline_performance', 'single_address', 100, 4.5, 45.0, 22.2, 0.98, 0.87,
 '15.0', '3.3', '{"memory": "1GB", "cpu_cores": 2}'),

('batch_performance', 'batch_processing', 1000, 18.5, 18.5, 54.1, 0.96, 0.84,
 '15.0', '3.3', '{"memory": "1GB", "cpu_cores": 2}'),

('concurrent_performance', 'concurrency', 500, 12.3, 24.6, 40.7, 0.94, 0.82,
 '15.0', '3.3', '{"memory": "1GB", "cpu_cores": 2, "concurrent_tasks": 20}');

-- Create some geographic regions for testing spatial queries
-- Turkish metropolitan area boundaries (simplified)
INSERT INTO turkish_admin_hierarchy (
    il_code, il_name, bounds, center_point, area_km2
) VALUES
('34', 'İstanbul', 
 ST_SetSRID(ST_GeomFromText('POLYGON((28.5 40.8, 29.8 40.8, 29.8 41.3, 28.5 41.3, 28.5 40.8))'), 4326),
 ST_SetSRID(ST_Point(29.15, 41.05), 4326), 5343.0),

('06', 'Ankara',
 ST_SetSRID(ST_GeomFromText('POLYGON((32.4 39.7, 33.2 39.7, 33.2 40.2, 32.4 40.2, 32.4 39.7))'), 4326),
 ST_SetSRID(ST_Point(32.8, 39.95), 4326), 25632.0),

('35', 'İzmir',
 ST_SetSRID(ST_GeomFromText('POLYGON((26.8 38.2, 27.5 38.2, 27.5 38.7, 26.8 38.7, 26.8 38.2))'), 4326),
 ST_SetSRID(ST_Point(27.15, 38.45), 4326), 11973.0);

-- Create custom functions for testing

-- Function to calculate address density in a region
CREATE OR REPLACE FUNCTION get_address_density(region_center GEOMETRY, radius_meters INTEGER)
RETURNS TABLE(
    center_lat FLOAT,
    center_lon FLOAT,
    radius_m INTEGER,
    address_count BIGINT,
    density_per_km2 FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ST_Y(region_center) as center_lat,
        ST_X(region_center) as center_lon,
        radius_meters as radius_m,
        COUNT(*) as address_count,
        (COUNT(*) * 1000000.0 / (PI() * radius_meters * radius_meters)) as density_per_km2
    FROM addresses 
    WHERE ST_DWithin(coordinates::geography, region_center::geography, radius_meters);
END;
$$ LANGUAGE plpgsql;

-- Function to find addresses within administrative boundary
CREATE OR REPLACE FUNCTION find_addresses_in_admin_boundary(
    p_il VARCHAR DEFAULT NULL,
    p_ilce VARCHAR DEFAULT NULL,
    p_mahalle VARCHAR DEFAULT NULL
)
RETURNS TABLE(
    address_id INTEGER,
    raw_address TEXT,
    confidence_score FLOAT,
    distance_from_center FLOAT
) AS $$
DECLARE
    boundary_geom GEOMETRY;
    center_geom GEOMETRY;
BEGIN
    -- Get boundary geometry based on administrative level
    IF p_mahalle IS NOT NULL THEN
        SELECT bounds, center_point INTO boundary_geom, center_geom
        FROM turkish_admin_hierarchy 
        WHERE il_name = p_il AND ilce_name = p_ilce AND mahalle_name = p_mahalle
        LIMIT 1;
    ELSIF p_ilce IS NOT NULL THEN
        SELECT bounds, center_point INTO boundary_geom, center_geom
        FROM turkish_admin_hierarchy 
        WHERE il_name = p_il AND ilce_name = p_ilce AND mahalle_name IS NULL
        LIMIT 1;
    ELSE
        SELECT bounds, center_point INTO boundary_geom, center_geom
        FROM turkish_admin_hierarchy 
        WHERE il_name = p_il AND ilce_name IS NULL
        LIMIT 1;
    END IF;
    
    -- Return addresses within boundary
    RETURN QUERY
    SELECT 
        a.id as address_id,
        a.raw_address,
        a.confidence_score,
        CASE 
            WHEN center_geom IS NOT NULL THEN 
                ST_Distance(a.coordinates::geography, center_geom::geography)
            ELSE NULL
        END as distance_from_center
    FROM addresses a
    WHERE (boundary_geom IS NULL OR ST_Within(a.coordinates, boundary_geom))
    ORDER BY distance_from_center NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Update statistics for optimal query performance
ANALYZE addresses;
ANALYZE turkish_admin_hierarchy;
ANALYZE address_processing_log;
ANALYZE performance_benchmarks;

-- Log successful data insertion
DO $$
DECLARE
    address_count INTEGER;
    hierarchy_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO address_count FROM addresses;
    SELECT COUNT(*) INTO hierarchy_count FROM turkish_admin_hierarchy;
    
    RAISE NOTICE 'Sample data successfully inserted for TEKNOFEST 2025';
    RAISE NOTICE 'Addresses inserted: %', address_count;
    RAISE NOTICE 'Admin hierarchy records: %', hierarchy_count;
    RAISE NOTICE 'Custom functions created: get_address_density, find_addresses_in_admin_boundary';
    RAISE NOTICE 'Database ready for integration testing!';
END $$;