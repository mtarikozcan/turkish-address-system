#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URGENT: Create Enhanced Turkish Neighborhood Database
Combine traditional (355) + OSM (55,600) data into unified format for system integration
"""

import pandas as pd
import sys
from pathlib import Path

def create_enhanced_database():
    """Create enhanced database combining traditional + OSM data"""
    
    print("🚨 URGENT: Creating Enhanced Turkish Neighborhood Database")
    print("=" * 60)
    
    enhanced_records = []
    
    # 1. Load traditional data (355 famous neighborhoods)
    print("📚 Loading traditional administrative data...")
    traditional_path = Path("database/turkey_admin_hierarchy.csv")
    
    if traditional_path.exists():
        traditional_df = pd.read_csv(traditional_path)
        print(f"   Loaded {len(traditional_df):,} traditional records")
        
        # Add traditional records to enhanced database
        for _, row in traditional_df.iterrows():
            enhanced_records.append({
                'il_kodu': row['il_kodu'],
                'il_adi': row['il_adi'],
                'ilce_kodu': row['ilce_kodu'],
                'ilce_adi': row['ilce_adi'],
                'mahalle_kodu': row['mahalle_kodu'],
                'mahalle_adi': row['mahalle_adi'],
                'source': 'traditional',
                'latitude': 0,  # Traditional data doesn't have coordinates
                'longitude': 0,
                'place_type': 'administrative'
            })
    else:
        print("❌ Traditional data file not found!")
    
    # 2. Load OSM neighborhood data (55,600 locations)
    print("🗺️  Loading OSM neighborhood data...")
    osm_path = Path("processed_osm_data/neighborhoods_turkey.csv")
    
    if osm_path.exists():
        osm_df = pd.read_csv(osm_path)
        print(f"   Loaded {len(osm_df):,} OSM neighborhoods")
        
        # Add OSM records to enhanced database
        for _, row in osm_df.iterrows():
            # Generate synthetic codes for OSM data
            synthetic_code = 90000 + len(enhanced_records)  # Start from 90000 to avoid conflicts
            
            enhanced_records.append({
                'il_kodu': 0,  # OSM data doesn't have province codes - will need mapping
                'il_adi': 'Unknown',  # OSM data doesn't have province info - will need mapping
                'ilce_kodu': 0,  # OSM data doesn't have district codes
                'ilce_adi': 'Unknown',  # OSM data doesn't have district info
                'mahalle_kodu': synthetic_code,
                'mahalle_adi': row['name'],
                'source': 'osm',
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'place_type': row['place_type']
            })
    else:
        print("❌ OSM neighborhoods file not found!")
    
    # 3. Create enhanced database
    print("🔧 Creating enhanced database...")
    enhanced_df = pd.DataFrame(enhanced_records)
    
    # Save enhanced database
    output_path = Path("database/enhanced_turkish_neighborhoods.csv")
    enhanced_df.to_csv(output_path, index=False)
    
    print(f"✅ Enhanced database created: {output_path}")
    print(f"   Total records: {len(enhanced_df):,}")
    print(f"   Traditional: {len([r for r in enhanced_records if r['source'] == 'traditional']):,}")
    print(f"   OSM: {len([r for r in enhanced_records if r['source'] == 'osm']):,}")
    
    # 4. Create streets database
    print("🛣️  Creating streets database...")
    streets_path = Path("processed_osm_data/streets_turkey.csv")
    
    if streets_path.exists():
        streets_df = pd.read_csv(streets_path)
        output_streets_path = Path("database/turkish_major_streets.csv")
        streets_df.to_csv(output_streets_path, index=False)
        print(f"✅ Streets database created: {output_streets_path}")
        print(f"   Total streets: {len(streets_df):,}")
    
    return len(enhanced_df)

if __name__ == "__main__":
    total_records = create_enhanced_database()
    print(f"\n🎯 SUCCESS: Enhanced database with {total_records:,} records ready for integration!")