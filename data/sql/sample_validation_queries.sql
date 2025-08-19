-- TEKNOFEST 2025 Adres Çözümleme Sistemi
-- Sample Validation Queries for Turkish Administrative Hierarchy
-- File: database/sample_validation_queries.sql

-- Test queries to validate turkey_admin_hierarchy.csv data
-- These queries can be used to test the AddressValidator algorithm

-- 1. Count total records
SELECT COUNT(*) as total_records FROM turkey_admin_hierarchy;
-- Expected: ~400+ records in our sample dataset

-- 2. Count unique provinces (should be 81)
SELECT COUNT(DISTINCT il_kodu) as unique_provinces,
       COUNT(DISTINCT il_adi) as unique_province_names
FROM turkey_admin_hierarchy;

-- 3. Count districts and neighborhoods
SELECT 
    COUNT(DISTINCT CONCAT(il_kodu, '-', ilce_kodu)) as unique_districts,
    COUNT(DISTINCT CONCAT(il_kodu, '-', ilce_kodu, '-', mahalle_kodu)) as unique_neighborhoods
FROM turkey_admin_hierarchy;

-- 4. ISTANBUL validation samples
-- Check Istanbul districts and neighborhoods
SELECT il_adi, ilce_adi, COUNT(*) as mahalle_count
FROM turkey_admin_hierarchy 
WHERE il_adi = 'İstanbul' 
GROUP BY il_adi, ilce_adi 
ORDER BY mahalle_count DESC;

-- Specific Istanbul neighborhood validation
SELECT * FROM turkey_admin_hierarchy 
WHERE il_adi = 'İstanbul' 
  AND ilce_adi = 'Kadıköy' 
  AND mahalle_adi LIKE '%Moda%';

SELECT * FROM turkey_admin_hierarchy 
WHERE il_adi = 'İstanbul' 
  AND ilce_adi = 'Beşiktaş' 
  AND mahalle_adi LIKE '%Levent%';

SELECT * FROM turkey_admin_hierarchy 
WHERE il_adi = 'İstanbul' 
  AND ilce_adi = 'Şişli' 
  AND mahalle_adi LIKE '%Mecidiyeköy%';

-- 5. ANKARA validation samples
SELECT il_adi, ilce_adi, COUNT(*) as mahalle_count
FROM turkey_admin_hierarchy 
WHERE il_adi = 'Ankara' 
GROUP BY il_adi, ilce_adi 
ORDER BY mahalle_count DESC;

-- Specific Ankara neighborhood validation
SELECT * FROM turkey_admin_hierarchy 
WHERE il_adi = 'Ankara' 
  AND ilce_adi = 'Çankaya' 
  AND mahalle_adi LIKE '%Kızılay%';

SELECT * FROM turkey_admin_hierarchy 
WHERE il_adi = 'Ankara' 
  AND ilce_adi = 'Çankaya' 
  AND mahalle_adi LIKE '%Bahçelievler%';

-- 6. IZMIR validation samples
SELECT il_adi, ilce_adi, COUNT(*) as mahalle_count
FROM turkey_admin_hierarchy 
WHERE il_adi = 'İzmir' 
GROUP BY il_adi, ilce_adi 
ORDER BY mahalle_count DESC;

-- Specific Izmir neighborhood validation
SELECT * FROM turkey_admin_hierarchy 
WHERE il_adi = 'İzmir' 
  AND ilce_adi = 'Konak' 
  AND mahalle_adi LIKE '%Alsancak%';

SELECT * FROM turkey_admin_hierarchy 
WHERE il_adi = 'İzmir' 
  AND ilce_adi = 'Karşıyaka' 
  AND mahalle_adi LIKE '%Bostanlı%';

-- 7. Hierarchy validation tests
-- Test for valid hierarchy relationships
SELECT 
    h1.il_adi,
    h1.ilce_adi,
    COUNT(DISTINCT h1.mahalle_adi) as mahalle_count
FROM turkey_admin_hierarchy h1
WHERE h1.il_adi IN ('İstanbul', 'Ankara', 'İzmir')
GROUP BY h1.il_adi, h1.ilce_adi
HAVING COUNT(DISTINCT h1.mahalle_adi) > 2
ORDER BY h1.il_adi, mahalle_count DESC;

-- 8. Turkish character validation
-- Find records with Turkish characters (ç, ğ, ı, ö, ş, ü)
SELECT il_adi, ilce_adi, mahalle_adi
FROM turkey_admin_hierarchy
WHERE il_adi LIKE '%ğ%' 
   OR il_adi LIKE '%ü%' 
   OR il_adi LIKE '%ş%' 
   OR il_adi LIKE '%ı%' 
   OR il_adi LIKE '%ö%' 
   OR il_adi LIKE '%ç%'
   OR ilce_adi LIKE '%ğ%' 
   OR ilce_adi LIKE '%ü%' 
   OR ilce_adi LIKE '%ş%' 
   OR ilce_adi LIKE '%ı%' 
   OR ilce_adi LIKE '%ö%' 
   OR ilce_adi LIKE '%ç%'
   OR mahalle_adi LIKE '%ğ%' 
   OR mahalle_adi LIKE '%ü%' 
   OR mahalle_adi LIKE '%ş%' 
   OR mahalle_adi LIKE '%ı%' 
   OR mahalle_adi LIKE '%ö%' 
   OR mahalle_adi LIKE '%ç%'
LIMIT 10;

-- 9. Sample address validation test cases
-- These test cases can be used by AddressValidator algorithm

-- Test Case 1: Valid hierarchy
-- Input: "İstanbul Kadıköy Moda Mahallesi"
-- Expected: VALID (34-1-34001)

-- Test Case 2: Valid hierarchy  
-- Input: "Ankara Çankaya Kızılay Mahallesi"
-- Expected: VALID (6-1-6001)

-- Test Case 3: Valid hierarchy
-- Input: "İzmir Konak Alsancak Mahallesi"
-- Expected: VALID (35-1-35001)

-- Test Case 4: Invalid hierarchy
-- Input: "İstanbul Çankaya Kızılay Mahallesi" 
-- Expected: INVALID (Çankaya is in Ankara, not Istanbul)

-- Test Case 5: Invalid hierarchy
-- Input: "Ankara Kadıköy Moda Mahallesi"
-- Expected: INVALID (Kadıköy is in Istanbul, not Ankara)

-- 10. Performance test queries
-- These can be used to test database performance with indexes

-- Search by province
EXPLAIN ANALYZE
SELECT * FROM turkey_admin_hierarchy WHERE il_adi = 'İstanbul';

-- Search by district
EXPLAIN ANALYZE  
SELECT * FROM turkey_admin_hierarchy 
WHERE il_adi = 'İstanbul' AND ilce_adi = 'Kadıköy';

-- Search by neighborhood
EXPLAIN ANALYZE
SELECT * FROM turkey_admin_hierarchy 
WHERE il_adi = 'İstanbul' 
  AND ilce_adi = 'Kadıköy' 
  AND mahalle_adi = 'Moda Mahallesi';

-- Fuzzy search simulation
SELECT * FROM turkey_admin_hierarchy 
WHERE LOWER(mahalle_adi) LIKE LOWER('%moda%') 
   OR LOWER(mahalle_adi) LIKE LOWER('%mecidiyeköy%')
   OR LOWER(mahalle_adi) LIKE LOWER('%alsancak%');

-- 11. Data quality checks
-- Check for potential data issues

-- Find duplicate entries
SELECT il_kodu, il_adi, ilce_kodu, ilce_adi, mahalle_kodu, mahalle_adi, COUNT(*)
FROM turkey_admin_hierarchy
GROUP BY il_kodu, il_adi, ilce_kodu, ilce_adi, mahalle_kodu, mahalle_adi
HAVING COUNT(*) > 1;

-- Find missing or empty values
SELECT 
    COUNT(*) as total_records,
    COUNT(CASE WHEN il_adi IS NULL OR il_adi = '' THEN 1 END) as empty_il,
    COUNT(CASE WHEN ilce_adi IS NULL OR ilce_adi = '' THEN 1 END) as empty_ilce,
    COUNT(CASE WHEN mahalle_adi IS NULL OR mahalle_adi = '' THEN 1 END) as empty_mahalle
FROM turkey_admin_hierarchy;

-- Find inconsistent naming patterns
SELECT il_adi, COUNT(DISTINCT ilce_adi) as ilce_count
FROM turkey_admin_hierarchy 
GROUP BY il_adi 
ORDER BY ilce_count DESC 
LIMIT 10;

-- 12. Statistics for algorithm optimization
-- These stats can help optimize the AddressValidator algorithm

-- Most common district names (for spell checking)
SELECT ilce_adi, COUNT(*) as frequency
FROM turkey_admin_hierarchy 
GROUP BY ilce_adi 
ORDER BY frequency DESC 
LIMIT 20;

-- Most common neighborhood name patterns
SELECT 
    CASE 
        WHEN mahalle_adi LIKE '%Mahallesi' THEN 'Mahallesi suffix'
        WHEN mahalle_adi LIKE '%Mahalle' THEN 'Mahalle suffix'  
        WHEN mahalle_adi LIKE 'Merkez%' THEN 'Merkez prefix'
        WHEN mahalle_adi LIKE '%Cumhuriyet%' THEN 'Cumhuriyet pattern'
        WHEN mahalle_adi LIKE '%Atatürk%' THEN 'Atatürk pattern'
        ELSE 'Other patterns'
    END as name_pattern,
    COUNT(*) as frequency
FROM turkey_admin_hierarchy 
GROUP BY name_pattern 
ORDER BY frequency DESC;