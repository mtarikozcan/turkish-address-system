-- TEKNOFEST 2025 Turkish Address Resolution System
-- Database Initialization Script 3: Test Data Insertion
-- 
-- This script inserts test data for Turkish addresses including
-- major cities, districts, and neighborhoods for integration testing.

-- Insert Turkish administrative hierarchy test data
INSERT INTO administrative_hierarchy (il, ilce, mahalle, bounds) VALUES
-- İstanbul districts
('İstanbul', 'Kadıköy', 'Moda', ST_MakeEnvelope(29.02, 40.97, 29.05, 41.00, 4326)),
('İstanbul', 'Kadıköy', 'Caferağa', ST_MakeEnvelope(29.02, 40.98, 29.04, 41.00, 4326)),
('İstanbul', 'Kadıköy', 'Fenerbahçe', ST_MakeEnvelope(29.03, 40.96, 29.06, 40.99, 4326)),
('İstanbul', 'Beşiktaş', 'Levent', ST_MakeEnvelope(29.00, 41.07, 29.03, 41.10, 4326)),
('İstanbul', 'Beşiktaş', 'Bebek', ST_MakeEnvelope(29.04, 41.07, 29.06, 41.09, 4326)),
('İstanbul', 'Şişli', 'Mecidiyeköy', ST_MakeEnvelope(28.99, 41.06, 29.02, 41.08, 4326)),

-- Ankara districts
('Ankara', 'Çankaya', 'Kızılay', ST_MakeEnvelope(32.84, 39.91, 32.86, 39.93, 4326)),
('Ankara', 'Çankaya', 'Bahçelievler', ST_MakeEnvelope(32.83, 39.90, 32.85, 39.92, 4326)),
('Ankara', 'Yenimahalle', 'Batıkent', ST_MakeEnvelope(32.73, 39.96, 32.76, 39.99, 4326)),

-- İzmir districts
('İzmir', 'Konak', 'Alsancak', ST_MakeEnvelope(27.12, 38.41, 27.15, 38.44, 4326)),
('İzmir', 'Konak', 'Güzelyalı', ST_MakeEnvelope(27.10, 38.39, 27.13, 38.42, 4326)),
('İzmir', 'Karşıyaka', 'Bostanlı', ST_MakeEnvelope(27.09, 38.45, 27.12, 38.48, 4326)),

-- Other major cities
('Bursa', 'Osmangazi', 'Soğanlı', ST_MakeEnvelope(29.04, 40.17, 29.08, 40.20, 4326)),
('Antalya', 'Muratpaşa', 'Lara', ST_MakeEnvelope(30.77, 36.82, 30.82, 36.85, 4326)),
('Gaziantep', 'Şahinbey', 'İnönü', ST_MakeEnvelope(37.36, 37.05, 37.40, 37.08, 4326))
ON CONFLICT (il, ilce, mahalle) DO NOTHING;

-- Insert Turkish abbreviations
INSERT INTO turkish_abbreviations (abbreviation, full_form, category) VALUES
('Mah.', 'Mahallesi', 'administrative'),
('Cd.', 'Caddesi', 'street_type'),
('Sk.', 'Sokak', 'street_type'),
('Blv.', 'Bulvarı', 'street_type'),
('Apt.', 'Apartmanı', 'building'),
('No:', 'Numara', 'number'),
('Kat:', 'Kat', 'floor'),
('D:', 'Daire', 'unit')
ON CONFLICT (abbreviation) DO NOTHING;

-- Insert common Turkish address errors
INSERT INTO turkish_common_errors (error_pattern, correct_form, error_type) VALUES
('istanbul', 'İstanbul', 'capitalization'),
('ankara', 'Ankara', 'capitalization'),
('izmir', 'İzmir', 'capitalization'),
('besiktas', 'Beşiktaş', 'turkish_chars'),
('sisli', 'Şişli', 'turkish_chars'),
('cankaya', 'Çankaya', 'turkish_chars'),
('kadikoy', 'Kadıköy', 'turkish_chars'),
('mahallesi', 'Mahallesi', 'spelling'),
('sokak', 'Sokak', 'spelling'),
('cadde', 'Caddesi', 'suffix')
ON CONFLICT (error_pattern) DO NOTHING;

-- Insert test addresses for validation
INSERT INTO addresses (
    raw_address, 
    normalized_address,
    corrected_address,
    parsed_components,
    coordinates,
    confidence_score,
    validation_status,
    processing_metadata
) VALUES
-- İstanbul test addresses
(
    'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
    'istanbul kadıköy moda mahallesi caferağa sokak no 10',
    'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
    '{"il": "İstanbul", "ilce": "Kadıköy", "mahalle": "Moda Mahallesi", "sokak": "Caferağa Sokak", "bina_no": "10"}'::jsonb,
    ST_SetSRID(ST_Point(29.0376, 40.9875), 4326),
    0.95,
    'valid',
    '{"test_data": true, "category": "residential"}'::jsonb
),
(
    'istanbul kadikoy moda mah caferaga sk 10',
    'istanbul kadikoy moda mah caferaga sk 10',
    'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
    '{"il": "İstanbul", "ilce": "Kadıköy", "mahalle": "Moda", "sokak": "Caferağa", "bina_no": "10"}'::jsonb,
    ST_SetSRID(ST_Point(29.0376, 40.9875), 4326),
    0.85,
    'valid',
    '{"test_data": true, "needs_correction": true}'::jsonb
),

-- Ankara test addresses
(
    'Ankara Çankaya Kızılay Mahallesi Atatürk Bulvarı 25',
    'ankara çankaya kızılay mahallesi atatürk bulvarı 25',
    'Ankara Çankaya Kızılay Mahallesi Atatürk Bulvarı 25',
    '{"il": "Ankara", "ilce": "Çankaya", "mahalle": "Kızılay Mahallesi", "bulvar": "Atatürk Bulvarı", "bina_no": "25"}'::jsonb,
    ST_SetSRID(ST_Point(32.8541, 39.9208), 4326),
    0.95,
    'valid',
    '{"test_data": true, "category": "commercial"}'::jsonb
),

-- İzmir test addresses
(
    'İzmir Konak Alsancak Mahallesi Cumhuriyet Bulvarı 45',
    'izmir konak alsancak mahallesi cumhuriyet bulvarı 45',
    'İzmir Konak Alsancak Mahallesi Cumhuriyet Bulvarı 45',
    '{"il": "İzmir", "ilce": "Konak", "mahalle": "Alsancak Mahallesi", "bulvar": "Cumhuriyet Bulvarı", "bina_no": "45"}'::jsonb,
    ST_SetSRID(ST_Point(27.1284, 38.4189), 4326),
    0.95,
    'valid',
    '{"test_data": true, "category": "commercial"}'::jsonb
),

-- Partial addresses for testing
(
    'Bursa Osmangazi Soğanlı Mahallesi',
    'bursa osmangazi soğanlı mahallesi',
    'Bursa Osmangazi Soğanlı Mahallesi',
    '{"il": "Bursa", "ilce": "Osmangazi", "mahalle": "Soğanlı Mahallesi"}'::jsonb,
    ST_SetSRID(ST_Point(29.0610, 40.1885), 4326),
    0.75,
    'valid',
    '{"test_data": true, "category": "incomplete", "missing": ["sokak", "bina_no"]}'::jsonb
)
ON CONFLICT DO NOTHING;

-- Insert Turkish POIs for testing
INSERT INTO turkish_pois (name, category, il, ilce, coordinates, metadata) VALUES
('Galata Kulesi', 'landmark', 'İstanbul', 'Beyoğlu', ST_SetSRID(ST_Point(28.9741, 41.0256), 4326), '{"visitor_count": 1000000}'::jsonb),
('Anıtkabir', 'landmark', 'Ankara', 'Çankaya', ST_SetSRID(ST_Point(32.8368, 39.9251), 4326), '{"visitor_count": 5000000}'::jsonb),
('Saat Kulesi', 'landmark', 'İzmir', 'Konak', ST_SetSRID(ST_Point(27.1287, 38.4192), 4326), '{"visitor_count": 2000000}'::jsonb),
('Güllüoğlu Baklava', 'business', 'Gaziantep', 'Şahinbey', ST_SetSRID(ST_Point(37.3833, 37.0662), 4326), '{"famous_for": "baklava"}'::jsonb)
ON CONFLICT DO NOTHING;

-- Create spatial index clusters for performance
CLUSTER addresses USING idx_addresses_coordinates;

-- Update table statistics
ANALYZE addresses;
ANALYZE administrative_hierarchy;
ANALYZE turkish_abbreviations;
ANALYZE turkish_common_errors;
ANALYZE turkish_pois;

-- Log successful data insertion
DO $$
DECLARE
    address_count INTEGER;
    hierarchy_count INTEGER;
    poi_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO address_count FROM addresses;
    SELECT COUNT(*) INTO hierarchy_count FROM administrative_hierarchy;
    SELECT COUNT(*) INTO poi_count FROM turkish_pois;
    
    RAISE NOTICE 'Test data successfully inserted:';
    RAISE NOTICE '  - % addresses', address_count;
    RAISE NOTICE '  - % administrative areas', hierarchy_count;
    RAISE NOTICE '  - % points of interest', poi_count;
END $$;