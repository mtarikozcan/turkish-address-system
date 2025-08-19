#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turkish Address System - OpenStreetMap Data Processor

Phase 3.5: System Optimization & Turkey Dataset Integration
Processes turkey-latest-free.shp.zip to extract Turkish neighborhoods and streets

Requirements:
- geopandas
- shapely  
- pandas
- fiona

Expected Input: turkey-latest-free.shp.zip (OpenStreetMap Turkey extract)
Expected Output: Enhanced turkey_admin_hierarchy.csv with 50,000+ locations
"""

import os
import sys
import zipfile
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import json

try:
    import geopandas as gpd
    import fiona
    from shapely.geometry import Point, Polygon
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    print("⚠️  GeoPandas not available. Install with: pip install geopandas")
    GEOSPATIAL_AVAILABLE = False

# Add src to Python path for imports
sys.path.append(str(Path(__file__).parent))
from turkish_text_utils import TurkishTextNormalizer


class OSMTurkeyProcessor:
    """
    OpenStreetMap Turkey Dataset Processor for Address System
    
    Extracts and processes Turkish geographic data from OSM shapefiles:
    - Administrative boundaries (il, ilçe, mahalle)
    - Streets and roads (sokak, cadde, bulvar)  
    - Points of interest and landmarks
    - Geographic coordinates for validation
    """
    
    def __init__(self, data_dir: str = "data/osm"):
        """
        Initialize OSM data processor
        
        Args:
            data_dir: Directory to store extracted OSM data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Data containers
        self.administrative_data = []
        self.street_data = []
        self.poi_data = []
        
        self.logger.info("OSMTurkeyProcessor initialized")
    
    def extract_shapefile_archive(self, zip_path: str) -> List[str]:
        """
        Extract turkey-latest-free.shp.zip and return shapefile paths
        
        Args:
            zip_path: Path to OSM Turkey ZIP archive
            
        Returns:
            List of extracted shapefile paths
        """
        try:
            if not os.path.exists(zip_path):
                raise FileNotFoundError(f"OSM archive not found: {zip_path}")
            
            extract_dir = self.data_dir / "extracted"
            extract_dir.mkdir(exist_ok=True)
            
            self.logger.info(f"Extracting OSM archive: {zip_path}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find all .shp files
            shp_files = list(extract_dir.rglob("*.shp"))
            self.logger.info(f"Found {len(shp_files)} shapefile layers")
            
            return [str(f) for f in shp_files]
            
        except Exception as e:
            self.logger.error(f"Error extracting shapefile archive: {e}")
            return []
    
    def analyze_shapefile_layers(self, shp_paths: List[str]) -> Dict[str, Dict]:
        """
        Analyze OSM shapefile layers to understand data structure
        
        Args:
            shp_paths: List of shapefile paths
            
        Returns:
            Dictionary with layer analysis results
        """
        if not GEOSPATIAL_AVAILABLE:
            self.logger.error("GeoPandas not available for shapefile processing")
            return {}
        
        layer_info = {}
        
        for shp_path in shp_paths:
            try:
                layer_name = Path(shp_path).stem
                self.logger.info(f"Analyzing layer: {layer_name}")
                
                # Read shapefile metadata
                with fiona.open(shp_path) as src:
                    schema = src.schema
                    crs = src.crs
                    bounds = src.bounds
                    count = len(src)
                
                # Sample first few records to understand content
                gdf = gpd.read_file(shp_path).head(10)
                
                layer_info[layer_name] = {
                    'path': shp_path,
                    'geometry_type': schema['geometry'],
                    'properties': list(schema['properties'].keys()),
                    'crs': crs,
                    'bounds': bounds,
                    'feature_count': count,
                    'sample_data': gdf.to_dict('records') if not gdf.empty else []
                }
                
                self.logger.info(f"  - Geometry: {schema['geometry']}")
                self.logger.info(f"  - Features: {count:,}")
                self.logger.info(f"  - Properties: {len(schema['properties'])} fields")
                
            except Exception as e:
                self.logger.error(f"Error analyzing {shp_path}: {e}")
                continue
        
        return layer_info
    
    def extract_turkish_places(self, layer_info: Dict[str, Dict]) -> List[Dict]:
        """
        Extract Turkish administrative places from OSM data
        
        Args:
            layer_info: Layer analysis results
            
        Returns:
            List of Turkish place records
        """
        if not GEOSPATIAL_AVAILABLE:
            return []
        
        places = []
        
        # Look for layers that contain place/boundary information
        place_layers = [
            name for name in layer_info.keys() 
            if any(keyword in name.lower() for keyword in 
                  ['place', 'boundary', 'admin', 'polygon'])
        ]
        
        self.logger.info(f"Processing {len(place_layers)} place layers")
        
        for layer_name in place_layers:
            try:
                layer = layer_info[layer_name]
                gdf = gpd.read_file(layer['path'])
                
                # Filter for Turkish places
                if 'name' in gdf.columns:
                    # Look for places with Turkish names or in Turkey bounds
                    turkish_places = gdf[
                        (gdf['name'].notna()) & 
                        (gdf.geometry.bounds.minx > 26) &  # Turkey longitude bounds
                        (gdf.geometry.bounds.maxx < 45) &
                        (gdf.geometry.bounds.miny > 36) &  # Turkey latitude bounds  
                        (gdf.geometry.bounds.maxy < 42)
                    ]
                    
                    for _, row in turkish_places.iterrows():
                        places.append({
                            'name': row.get('name', ''),
                            'name_tr': row.get('name:tr', ''),
                            'admin_level': row.get('admin_level', ''),
                            'place_type': row.get('place', ''),
                            'geometry_type': str(row.geometry.geom_type),
                            'bounds': row.geometry.bounds,
                            'layer': layer_name
                        })
                
            except Exception as e:
                self.logger.error(f"Error processing layer {layer_name}: {e}")
                continue
        
        self.logger.info(f"Extracted {len(places)} Turkish places")
        return places
    
    def extract_turkish_roads(self, layer_info: Dict[str, Dict]) -> List[Dict]:
        """
        Extract Turkish roads and streets from OSM data
        
        Args:
            layer_info: Layer analysis results
            
        Returns:
            List of Turkish road records
        """
        if not GEOSPATIAL_AVAILABLE:
            return []
        
        roads = []
        
        # Look for layers that contain road/line information
        road_layers = [
            name for name in layer_info.keys() 
            if any(keyword in name.lower() for keyword in 
                  ['road', 'line', 'street', 'way'])
        ]
        
        self.logger.info(f"Processing {len(road_layers)} road layers")
        
        for layer_name in road_layers:
            try:
                layer = layer_info[layer_name]
                gdf = gpd.read_file(layer['path'])
                
                # Filter for Turkish roads
                if 'name' in gdf.columns:
                    # Look for roads with Turkish names or in Turkey bounds
                    turkish_roads = gdf[
                        (gdf['name'].notna()) & 
                        (gdf.geometry.bounds.minx > 26) &  # Turkey bounds
                        (gdf.geometry.bounds.maxx < 45) &
                        (gdf.geometry.bounds.miny > 36) &
                        (gdf.geometry.bounds.maxy < 42)
                    ]
                    
                    for _, row in turkish_roads.iterrows():
                        # Extract road type from name or highway tag
                        road_name = row.get('name', '')
                        highway_type = row.get('highway', '')
                        
                        # Categorize Turkish road types
                        road_type = self._categorize_turkish_road_type(road_name, highway_type)
                        
                        roads.append({
                            'name': road_name,
                            'name_tr': row.get('name:tr', ''),
                            'highway': highway_type,
                            'road_type': road_type,
                            'geometry_type': str(row.geometry.geom_type),
                            'bounds': row.geometry.bounds,
                            'layer': layer_name
                        })
                
            except Exception as e:
                self.logger.error(f"Error processing road layer {layer_name}: {e}")
                continue
        
        self.logger.info(f"Extracted {len(roads)} Turkish roads")
        return roads
    
    def _categorize_turkish_road_type(self, name: str, highway: str) -> str:
        """
        Categorize Turkish road types based on name patterns
        
        Args:
            name: Road name
            highway: OSM highway tag
            
        Returns:
            Turkish road type (sokak, cadde, bulvar, etc.)
        """
        if not name:
            return highway or 'unknown'
        
        name_lower = name.lower()
        
        # Turkish road type patterns
        if any(word in name_lower for word in ['sokak', 'sokağı', 'sk']):
            return 'sokak'
        elif any(word in name_lower for word in ['cadde', 'caddesi', 'cd']):
            return 'cadde'
        elif any(word in name_lower for word in ['bulvar', 'bulvarı', 'blv']):
            return 'bulvar'
        elif any(word in name_lower for word in ['yol', 'yolu']):
            return 'yol'
        elif any(word in name_lower for word in ['meydan', 'meydanı']):
            return 'meydan'
        else:
            return highway or 'yol'
    
    def process_osm_data(self, zip_path: str) -> Dict[str, any]:
        """
        Complete OSM data processing pipeline
        
        Args:
            zip_path: Path to turkey-latest-free.shp.zip
            
        Returns:
            Dictionary with processing results
        """
        self.logger.info("Starting OSM Turkey data processing pipeline")
        
        # Step 1: Extract shapefiles
        shp_paths = self.extract_shapefile_archive(zip_path)
        if not shp_paths:
            return {"error": "Failed to extract shapefiles"}
        
        # Step 2: Analyze layers
        layer_info = self.analyze_shapefile_layers(shp_paths)
        if not layer_info:
            return {"error": "Failed to analyze layers"}
        
        # Step 3: Extract places and roads
        places = self.extract_turkish_places(layer_info)
        roads = self.extract_turkish_roads(layer_info)
        
        # Step 4: Save results
        results = {
            "layers_analyzed": len(layer_info),
            "places_extracted": len(places),
            "roads_extracted": len(roads),
            "layer_info": layer_info,
            "places": places,
            "roads": roads
        }
        
        # Save to JSON for analysis
        results_path = self.data_dir / "osm_processing_results.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            # Convert non-serializable objects to strings
            serializable_results = self._make_json_serializable(results)
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Processing complete. Results saved to: {results_path}")
        return results
    
    def _make_json_serializable(self, obj):
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return list(obj)
        elif hasattr(obj, '__dict__'):
            return str(obj)
        else:
            return obj
    
    def enhance_hierarchy_csv(self, osm_results: Dict, current_csv_path: str) -> str:
        """
        Enhance existing turkey_admin_hierarchy.csv with OSM data
        
        Args:
            osm_results: Results from OSM processing
            current_csv_path: Path to existing CSV file
            
        Returns:
            Path to enhanced CSV file
        """
        self.logger.info("Enhancing turkey_admin_hierarchy.csv with OSM data")
        
        # Load existing data
        existing_df = pd.read_csv(current_csv_path)
        self.logger.info(f"Current CSV has {len(existing_df)} records")
        
        # Process OSM places into CSV format
        new_records = []
        places = osm_results.get('places', [])
        
        for place in places:
            # Extract administrative information
            name = place.get('name', '') or place.get('name_tr', '')
            if not name:
                continue
            
            # Determine administrative level
            admin_level = place.get('admin_level', '')
            place_type = place.get('place_type', '')
            
            # Map to Turkish administrative hierarchy
            il_adi, ilce_adi, mahalle_adi = self._map_to_turkish_admin(
                name, admin_level, place_type
            )
            
            if any([il_adi, ilce_adi, mahalle_adi]):
                new_records.append({
                    'il_kodu': 999,  # Placeholder - would need proper mapping
                    'il_adi': il_adi or '',
                    'ilce_kodu': 999,  # Placeholder
                    'ilce_adi': ilce_adi or '',  
                    'mahalle_kodu': 999,  # Placeholder
                    'mahalle_adi': mahalle_adi or '',
                    'source': 'OSM',
                    'osm_place_type': place_type,
                    'osm_admin_level': admin_level
                })
        
        self.logger.info(f"Generated {len(new_records)} new records from OSM data")
        
        # Create enhanced dataset
        if new_records:
            osm_df = pd.DataFrame(new_records)
            enhanced_df = pd.concat([existing_df, osm_df], ignore_index=True)
        else:
            enhanced_df = existing_df
        
        # Save enhanced CSV
        enhanced_path = current_csv_path.replace('.csv', '_enhanced_osm.csv')
        enhanced_df.to_csv(enhanced_path, index=False, encoding='utf-8')
        
        self.logger.info(f"Enhanced CSV saved: {enhanced_path}")
        self.logger.info(f"Total records: {len(existing_df)} → {len(enhanced_df)}")
        
        return enhanced_path
    
    def _map_to_turkish_admin(self, name: str, admin_level: str, place_type: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Map OSM place to Turkish administrative hierarchy
        
        Args:
            name: Place name
            admin_level: OSM admin_level
            place_type: OSM place type
            
        Returns:
            Tuple of (il, ilce, mahalle) or None values
        """
        # Normalize name
        normalized_name = TurkishTextNormalizer.turkish_title(name)
        
        # Map based on admin_level (OSM administrative levels for Turkey)
        if admin_level == '4':  # Province level
            return (normalized_name, None, None)
        elif admin_level == '6':  # District level  
            return (None, normalized_name, None)
        elif admin_level in ['8', '9', '10']:  # Neighborhood level
            return (None, None, normalized_name)
        elif place_type in ['city', 'town']:
            return (normalized_name, None, None)
        elif place_type in ['suburb', 'neighbourhood', 'quarter']:
            return (None, None, normalized_name)
        else:
            # Default to neighborhood for unclassified places
            return (None, None, normalized_name)


# CLI Interface
def main():
    """Command line interface for OSM processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process OSM Turkey dataset for Address System')
    parser.add_argument('--zip', required=True, help='Path to turkey-latest-free.shp.zip')
    parser.add_argument('--csv', help='Path to existing turkey_admin_hierarchy.csv')
    parser.add_argument('--data-dir', default='data/osm', help='Data directory for OSM processing')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = OSMTurkeyProcessor(args.data_dir)
    
    # Process OSM data
    results = processor.process_osm_data(args.zip)
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return 1
    
    # Print summary
    print(f"\n🗺️  OSM Turkey Processing Complete!")
    print(f"Layers analyzed: {results['layers_analyzed']}")
    print(f"🏙️  Places extracted: {results['places_extracted']:,}")
    print(f"🛣️  Roads extracted: {results['roads_extracted']:,}")
    
    # Enhance CSV if provided
    if args.csv and os.path.exists(args.csv):
        enhanced_path = processor.enhance_hierarchy_csv(results, args.csv)
        print(f"✅ Enhanced CSV: {enhanced_path}")
    
    print(f"\nReady for Phase 3.5 integration!")
    return 0


if __name__ == "__main__":
    exit(main())