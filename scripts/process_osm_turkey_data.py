#!/usr/bin/env python3
"""
OpenStreetMap Turkey Data Processor for Address Resolution System Address System

This script processes the OpenStreetMap Turkey dataset to extract neighborhoods and streets
for building a comprehensive address database. It targets expanding from 355 sample records
to 50,000+ neighborhoods across Turkey.

Features:
- Extracts neighborhoods from OSM places data
- Extracts streets from OSM roads data
- Generates CSV files for database import
- Creates detailed summary reports
- Handles Turkish character encoding properly
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('osm_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OSMTurkeyProcessor:
    """Process OpenStreetMap Turkey dataset for address system."""
    
    def __init__(self, data_dir: str):
        """Initialize processor with data directory path."""
        self.data_dir = Path(data_dir)
        self.output_dir = Path("processed_osm_data")
        self.output_dir.mkdir(exist_ok=True)
        
        # Define target neighborhood types from OSM
        self.neighborhood_types = [
            'neighbourhood', 'suburb', 'quarter', 'hamlet', 
            'village', 'residential', 'city_block'
        ]
        
        # Define target street types from OSM
        self.street_types = [
            'residential', 'primary', 'secondary', 'tertiary',
            'trunk', 'living_street', 'pedestrian', 'service',
            'unclassified', 'primary_link', 'secondary_link', 'tertiary_link'
        ]
        
        logger.info(f"Initialized OSM Turkey Processor")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def load_places_data(self) -> gpd.GeoDataFrame:
        """Load and examine places shapefile."""
        places_file = self.data_dir / "gis_osm_places_free_1.shp"
        
        if not places_file.exists():
            raise FileNotFoundError(f"Places shapefile not found: {places_file}")
        
        logger.info(f"Loading places data from {places_file}")
        logger.info(f"File size: {places_file.stat().st_size / (1024*1024):.1f} MB")
        
        try:
            gdf = gpd.read_file(places_file)
            logger.info(f"Loaded {len(gdf)} place records")
            logger.info(f"Columns: {list(gdf.columns)}")
            
            # Check for place type column variations
            place_col = None
            for col in ['place', 'fclass', 'type']:
                if col in gdf.columns:
                    place_col = col
                    break
            
            if place_col:
                logger.info(f"Place types found in '{place_col}': {sorted(gdf[place_col].unique())}")
            
            return gdf
            
        except Exception as e:
            logger.error(f"Error loading places data: {e}")
            raise
    
    def load_roads_data(self) -> gpd.GeoDataFrame:
        """Load and examine roads shapefile."""
        roads_file = self.data_dir / "gis_osm_roads_free_1.shp"
        
        if not roads_file.exists():
            raise FileNotFoundError(f"Roads shapefile not found: {roads_file}")
        
        logger.info(f"Loading roads data from {roads_file}")
        logger.info(f"File size: {roads_file.stat().st_size / (1024*1024):.1f} MB")
        
        try:
            # Load in chunks if file is very large
            gdf = gpd.read_file(roads_file)
            logger.info(f"Loaded {len(gdf)} road records")
            logger.info(f"Columns: {list(gdf.columns)}")
            
            # Check for highway type column variations
            highway_col = None
            for col in ['highway', 'fclass', 'type']:
                if col in gdf.columns:
                    highway_col = col
                    break
            
            if highway_col:
                highway_types = gdf[highway_col].value_counts()
                logger.info(f"Highway types found in '{highway_col}':")
                for htype, count in highway_types.head(20).items():
                    logger.info(f"  {htype}: {count}")
            
            return gdf
            
        except Exception as e:
            logger.error(f"Error loading roads data: {e}")
            raise
    
    def extract_neighborhoods(self, places_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
        """Extract neighborhood data from places."""
        logger.info("Extracting neighborhoods from places data...")
        
        # Determine the correct column name for place types
        place_col = None
        for col in ['place', 'fclass', 'type']:
            if col in places_gdf.columns:
                place_col = col
                break
        
        if not place_col:
            logger.warning("No place type column found. Using all places.")
            neighborhoods = places_gdf.copy()
        else:
            # Filter for neighborhood-like places
            mask = places_gdf[place_col].isin(self.neighborhood_types)
            neighborhoods = places_gdf[mask].copy()
            logger.info(f"Found {len(neighborhoods)} neighborhoods after filtering by type")
        
        # Extract coordinates
        neighborhoods['longitude'] = neighborhoods.geometry.x
        neighborhoods['latitude'] = neighborhoods.geometry.y
        
        # Prepare output columns
        output_columns = {
            'name': 'name',
            'place_type': place_col if place_col else 'type',
            'latitude': 'latitude',
            'longitude': 'longitude'
        }
        
        # Add additional useful columns if they exist
        for col in ['population', 'admin_level', 'is_in']:
            if col in neighborhoods.columns:
                output_columns[col] = col
        
        # Create clean DataFrame
        result_data = []
        for idx, row in neighborhoods.iterrows():
            record = {}
            for output_col, source_col in output_columns.items():
                if source_col in row and pd.notna(row[source_col]):
                    record[output_col] = str(row[source_col]).strip()
                else:
                    record[output_col] = ''
            
            # Only include records with names
            if record.get('name'):
                result_data.append(record)
        
        result_df = pd.DataFrame(result_data)
        logger.info(f"Extracted {len(result_df)} named neighborhoods")
        
        # Show sample of extracted data
        if len(result_df) > 0:
            logger.info("Sample neighborhood records:")
            for i, row in result_df.head().iterrows():
                logger.info(f"  {row['name']} ({row.get('place_type', 'N/A')})")
        
        return result_df
    
    def extract_streets(self, roads_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
        """Extract street data from roads."""
        logger.info("Extracting streets from roads data...")
        
        # Determine the correct column name for highway types
        highway_col = None
        for col in ['highway', 'fclass', 'type']:
            if col in roads_gdf.columns:
                highway_col = col
                break
        
        if not highway_col:
            logger.warning("No highway type column found. Using all roads.")
            streets = roads_gdf.copy()
        else:
            # Filter for street-like roads
            mask = roads_gdf[highway_col].isin(self.street_types)
            streets = roads_gdf[mask].copy()
            logger.info(f"Found {len(streets)} streets after filtering by type")
        
        # Extract centroid coordinates for streets
        try:
            centroids = streets.geometry.centroid
            streets['longitude'] = centroids.x
            streets['latitude'] = centroids.y
        except Exception as e:
            logger.warning(f"Error calculating centroids: {e}")
            streets['longitude'] = 0.0
            streets['latitude'] = 0.0
        
        # Prepare output columns
        output_columns = {
            'name': 'name',
            'highway_type': highway_col if highway_col else 'type',
            'latitude': 'latitude',
            'longitude': 'longitude'
        }
        
        # Add additional useful columns if they exist
        for col in ['maxspeed', 'surface', 'lanes']:
            if col in streets.columns:
                output_columns[col] = col
        
        # Create clean DataFrame
        result_data = []
        for idx, row in streets.iterrows():
            record = {}
            for output_col, source_col in output_columns.items():
                if source_col in row and pd.notna(row[source_col]):
                    record[output_col] = str(row[source_col]).strip()
                else:
                    record[output_col] = ''
            
            # Only include records with names
            if record.get('name'):
                result_data.append(record)
        
        result_df = pd.DataFrame(result_data)
        logger.info(f"Extracted {len(result_df)} named streets")
        
        # Show sample of extracted data
        if len(result_df) > 0:
            logger.info("Sample street records:")
            for i, row in result_df.head().iterrows():
                logger.info(f"  {row['name']} ({row.get('highway_type', 'N/A')})")
        
        return result_df
    
    def save_to_csv(self, df: pd.DataFrame, filename: str):
        """Save DataFrame to CSV with proper encoding."""
        filepath = self.output_dir / filename
        try:
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"Saved {len(df)} records to {filepath}")
        except Exception as e:
            logger.error(f"Error saving to CSV {filepath}: {e}")
            raise
    
    def generate_summary_report(self, neighborhoods_df: pd.DataFrame, streets_df: pd.DataFrame):
        """Generate a comprehensive summary report."""
        logger.info("Generating summary report...")
        
        report_lines = [
            "# OpenStreetMap Turkey Dataset Processing Report",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Dataset Overview",
            f"- Source: OpenStreetMap Turkey (turkey-latest-free)",
            f"- Processing Date: {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## Extraction Results",
            "",
            "### Neighborhoods",
            f"- Total neighborhoods extracted: **{len(neighborhoods_df):,}**",
        ]
        
        if len(neighborhoods_df) > 0:
            # Neighborhood type breakdown
            if 'place_type' in neighborhoods_df.columns:
                type_counts = neighborhoods_df['place_type'].value_counts()
                report_lines.append("- Breakdown by type:")
                for place_type, count in type_counts.items():
                    report_lines.append(f"  - {place_type}: {count:,}")
            
            report_lines.extend([
                "",
                "### Sample Neighborhoods",
            ])
            
            for i, row in neighborhoods_df.head(10).iterrows():
                place_type = row.get('place_type', 'N/A')
                report_lines.append(f"- {row['name']} ({place_type})")
        
        report_lines.extend([
            "",
            "### Streets",
            f"- Total streets extracted: **{len(streets_df):,}**",
        ])
        
        if len(streets_df) > 0:
            # Street type breakdown
            if 'highway_type' in streets_df.columns:
                type_counts = streets_df['highway_type'].value_counts()
                report_lines.append("- Breakdown by type:")
                for highway_type, count in type_counts.head(10).items():
                    report_lines.append(f"  - {highway_type}: {count:,}")
            
            report_lines.extend([
                "",
                "### Sample Streets",
            ])
            
            for i, row in streets_df.head(10).iterrows():
                highway_type = row.get('highway_type', 'N/A')
                report_lines.append(f"- {row['name']} ({highway_type})")
        
        # Progress towards goal
        target_neighborhoods = 50000
        progress_percentage = min(100, (len(neighborhoods_df) / target_neighborhoods) * 100)
        
        report_lines.extend([
            "",
            "## Address Resolution System Address System Progress",
            f"- Target: {target_neighborhoods:,} neighborhoods",
            f"- Current: {len(neighborhoods_df):,} neighborhoods",
            f"- Progress: {progress_percentage:.1f}%",
            "",
            "## Output Files",
            f"- neighborhoods_turkey.csv: {len(neighborhoods_df):,} records",
            f"- streets_turkey.csv: {len(streets_df):,} records",
            "",
            "## Next Steps",
            "1. Import CSV files into the Address Resolution System address database",
            "2. Implement address matching algorithms",
            "3. Test with real address queries",
            "4. Fine-tune extraction criteria if needed"
        ])
        
        # Save report
        report_content = "\n".join(report_lines)
        report_path = self.output_dir / "processing_summary_report.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Summary report saved to {report_path}")
        except Exception as e:
            logger.error(f"Error saving summary report: {e}")
        
        # Also log key statistics
        logger.info("=== PROCESSING SUMMARY ===")
        logger.info(f"Neighborhoods extracted: {len(neighborhoods_df):,}")
        logger.info(f"Streets extracted: {len(streets_df):,}")
        logger.info(f"Progress towards 50k neighborhoods: {progress_percentage:.1f}%")
        logger.info("==========================")
    
    def process(self):
        """Main processing pipeline."""
        logger.info("Starting OpenStreetMap Turkey data processing...")
        
        try:
            # Load shapefiles
            places_gdf = self.load_places_data()
            roads_gdf = self.load_roads_data()
            
            # Extract data
            neighborhoods_df = self.extract_neighborhoods(places_gdf)
            streets_df = self.extract_streets(roads_gdf)
            
            # Save CSV files
            self.save_to_csv(neighborhoods_df, "neighborhoods_turkey.csv")
            self.save_to_csv(streets_df, "streets_turkey.csv")
            
            # Generate summary report
            self.generate_summary_report(neighborhoods_df, streets_df)
            
            logger.info("Processing completed successfully!")
            return neighborhoods_df, streets_df
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise

def main():
    """Main execution function."""
    try:
        # Initialize processor
        data_dir = "/Users/tarikozcan/Desktop/turkey-latest-free"
        processor = OSMTurkeyProcessor(data_dir)
        
        # Process the data
        neighborhoods, streets = processor.process()
        
        print(f"\n🎉 Processing completed successfully!")
        print(f"📍 Neighborhoods extracted: {len(neighborhoods):,}")
        print(f"🛣️  Streets extracted: {len(streets):,}")
        print(f"📁 Output files saved to: processed_osm_data/")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())