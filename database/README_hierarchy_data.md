# Turkish Administrative Hierarchy Data

## 📄 Files Created

### 1. turkey_admin_hierarchy.csv
**Location:** `database/turkey_admin_hierarchy.csv`
**Format:** CSV with UTF-8 encoding
**Purpose:** Address validation and hierarchy checking for AddressValidator algorithm

### 2. sample_validation_queries.sql  
**Location:** `database/sample_validation_queries.sql`
**Purpose:** Test queries and validation scenarios for the hierarchy data

## 📊 Data Statistics

- **Total Records:** 355 (including header)
- **Data Rows:** 354 administrative units
- **Provinces (İl):** All 81 Turkish provinces included
- **Major Cities Coverage:**
  - **İstanbul:** 35 districts with comprehensive neighborhoods
  - **Ankara:** 9 districts with key neighborhoods  
  - **İzmir:** 11 districts with major neighborhoods
- **Encoding:** UTF-8 with full Turkish character support (ç, ğ, ı, ö, ş, ü)

## 🏗️ Data Structure

```csv
il_kodu,il_adi,ilce_kodu,ilce_adi,mahalle_kodu,mahalle_adi
34,İstanbul,1,Kadıköy,34001,Moda Mahallesi
```

### Field Descriptions:
- **il_kodu:** Province plate code (1-81)
- **il_adi:** Province name in Turkish
- **ilce_kodu:** District code within province  
- **ilce_adi:** District name in Turkish
- **mahalle_kodu:** Neighborhood unique code
- **mahalle_adi:** Neighborhood name in Turkish

## 🎯 Usage in AddressValidator Algorithm

This data will be used by the `AddressValidator` class to:

1. **Hierarchy Validation:** Check if İl-İlçe-Mahalle relationships are valid
2. **Spelling Correction:** Provide reference names for fuzzy matching
3. **Administrative Completeness:** Verify address component consistency
4. **Turkish Character Handling:** Support proper Turkish text processing

### Example Validation Cases:

✅ **VALID:**
- "İstanbul Kadıköy Moda Mahallesi" → (34-1-34001)
- "Ankara Çankaya Kızılay Mahallesi" → (6-1-6001)
- "İzmir Konak Alsancak Mahallesi" → (35-1-35001)

❌ **INVALID:**
- "İstanbul Çankaya Kızılay Mahallesi" → Çankaya is in Ankara, not İstanbul
- "Ankara Kadıköy Moda Mahallesi" → Kadıköy is in İstanbul, not Ankara

## 📋 Major Cities Coverage

### İstanbul (Plate: 34)
**Districts:** Kadıköy, Beşiktaş, Şişli, Bakırköy, Fatih, Beyoğlu, Zeytinburnu, Esenler, Güngören, Bağcılar, Bahçelievler, Gaziosmanpaşa, Sultangazi, Arnavutköy, Eyüpsultan, Bayrampaşa, Avcılar, Küçükçekmece, Büyükçekmece, Çatalca, Silivri, Pendik, Tuzla, Kartal, Maltepe, Ataşehir, Ümraniye, Üsküdar, Beykoz, Şile, Çekmeköy, Sultanbeyli, Sancaktepe, Esenyurt, Başakşehir

**Key Neighborhoods:** Moda, Caferağa, Levent, Etiler, Mecidiyeköy, Taksim, Sultanahmet, Ataköy, etc.

### Ankara (Plate: 6)
**Districts:** Çankaya, Keçiören, Yenimahalle, Mamak, Sincan, Altındağ, Gölbaşı, Pursaklar, Etimesgut

**Key Neighborhoods:** Kızılay, Bahçelievler, Çukurambar, Balgat, Etlik, Batıkent, Ostim, Ulus, etc.

### İzmir (Plate: 35)  
**Districts:** Konak, Karşıyaka, Bornova, Buca, Gaziemir, Narlıdere, Balçova, Güzelbahçe, Bayraklı, Çiğli, Menemen

**Key Neighborhoods:** Alsancak, Bostanlı, Mavişehir, Şirinyer, etc.

## 🔧 Integration Instructions

### Loading Data in Python:
```python
import pandas as pd

# Load hierarchy data
hierarchy_df = pd.read_csv('database/turkey_admin_hierarchy.csv', encoding='utf-8')

# Create lookup dictionaries
province_lookup = hierarchy_df.groupby(['il_adi', 'ilce_adi'])['mahalle_adi'].apply(list).to_dict()
```

### Database Import:
```sql
-- Create table for hierarchy data
CREATE TABLE turkey_admin_hierarchy (
    il_kodu INTEGER,
    il_adi VARCHAR(50),
    ilce_kodu INTEGER, 
    ilce_adi VARCHAR(50),
    mahalle_kodu INTEGER,
    mahalle_adi VARCHAR(100)
);

-- Import CSV data
COPY turkey_admin_hierarchy FROM 'database/turkey_admin_hierarchy.csv' 
WITH CSV HEADER ENCODING 'UTF8';

-- Create indexes for performance
CREATE INDEX idx_hierarchy_il ON turkey_admin_hierarchy(il_adi);
CREATE INDEX idx_hierarchy_ilce ON turkey_admin_hierarchy(il_adi, ilce_adi);
CREATE INDEX idx_hierarchy_mahalle ON turkey_admin_hierarchy(il_adi, ilce_adi, mahalle_adi);
```

## 🧪 Testing & Validation

Use the provided `sample_validation_queries.sql` to:

1. **Data Quality Checks:** Verify completeness and consistency
2. **Performance Testing:** Test query speed with different indexes
3. **Turkish Character Validation:** Ensure proper encoding
4. **Hierarchy Logic Testing:** Validate parent-child relationships
5. **Address Validation Scenarios:** Test real-world address cases

## 🔄 Data Updates

This dataset represents a comprehensive sample for the TEKNOFEST competition. For production use:

1. **Regular Updates:** Administrative boundaries can change
2. **Extended Coverage:** Add more neighborhoods for smaller cities
3. **Postal Code Integration:** Enhance with postal code mappings
4. **Coordinate Data:** Add geographic coordinates for spatial validation

## 📚 Data Sources Reference

Based on:
- Turkish Statistical Institute (TÜİK) administrative divisions
- Official municipality records
- Open government data initiatives
- Current administrative hierarchy as of 2025

---

**Note:** This dataset is optimized for the TEKNOFEST address matching competition and provides sufficient coverage for algorithm development and testing.