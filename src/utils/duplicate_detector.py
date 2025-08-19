"""
TEKNOFEST 2025 - Duplicate Address Detection System
Algorithm 5: Duplicate Address Detector

TEKNOFEST REQUIREMENT: Find groups of duplicate addresses for competition
"""

import logging
import time
from typing import Dict, List, Tuple, Any, Set, Optional
from collections import defaultdict
import numpy as np
from itertools import combinations

# Import existing system components
try:
    from address_matcher import HybridAddressMatcher
    from address_parser import AddressParser
    from address_corrector import AddressCorrector
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False
    print("Warning: Core components not available, using fallback mode")


class DuplicateAddressDetector:
    """
    TEKNOFEST Duplicate Address Detection System
    
    Finds groups of addresses that refer to the same physical location
    but are written differently due to:
    - Spelling variations
    - Abbreviations vs full forms
    - Turkish character differences
    - Word order changes
    """
    
    def __init__(self, similarity_threshold: float = 0.75):
        """
        Initialize duplicate detector
        
        Args:
            similarity_threshold: Minimum similarity score to consider duplicates (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        if COMPONENTS_AVAILABLE:
            self.hybrid_matcher = HybridAddressMatcher()
            self.parser = AddressParser()
            self.corrector = AddressCorrector()
        else:
            self.hybrid_matcher = None
            self.parser = None
            self.corrector = None
            
        # Performance optimization: cache similarity calculations
        self._similarity_cache = {}
        self._normalization_cache = {}  # Cache normalized addresses
        
        self.logger.info("DuplicateAddressDetector initialized with threshold %.2f", similarity_threshold)
    
    def find_duplicate_groups(self, addresses: List[str]) -> List[List[int]]:
        """
        TEKNOFEST REQUIREMENT: Find groups of duplicate addresses
        
        Args:
            addresses: List of address strings to check for duplicates
            
        Returns:
            List of groups, where each group contains indices of duplicate addresses
            Example: [[0, 3, 7], [1, 5], [2], [4], [6]] 
            
        Algorithm:
            1. Compare all address pairs for similarity
            2. Create similarity matrix
            3. Use clustering to group similar addresses
            4. Return indices of duplicate groups
        """
        if not addresses:
            return []
        
        start_time = time.time()
        self.logger.info(f"Finding duplicate groups for {len(addresses)} addresses")
        
        # Step 1: Normalize all addresses first for better comparison (with caching)
        normalized_addresses = []
        for addr in addresses:
            # Check cache first for performance
            if addr in self._normalization_cache:
                normalized_addresses.append(self._normalization_cache[addr])
                continue
                
            try:
                if self.corrector:
                    corrected = self.corrector.correct_address(addr)
                    normalized = corrected['corrected_address']
                else:
                    normalized = addr.strip().lower()
                
                # Cache the result
                self._normalization_cache[addr] = normalized
                normalized_addresses.append(normalized)
            except Exception as e:
                self.logger.warning(f"Error normalizing address '{addr}': {e}")
                fallback = addr.strip()
                self._normalization_cache[addr] = fallback
                normalized_addresses.append(fallback)
        
        # Step 2: Build similarity matrix
        n = len(addresses)
        similarity_matrix = self._build_similarity_matrix(normalized_addresses)
        
        # Step 3: Find connected components (groups of similar addresses)
        duplicate_groups = self._cluster_similar_addresses(similarity_matrix, self.similarity_threshold)
        
        # Step 4: Filter out single-item groups (not duplicates)
        duplicate_groups = [group for group in duplicate_groups if len(group) > 1]
        
        # Step 5: Add remaining addresses as individual groups
        all_grouped_indices = set()
        for group in duplicate_groups:
            all_grouped_indices.update(group)
        
        # Add ungrouped addresses as individual groups
        for i in range(n):
            if i not in all_grouped_indices:
                duplicate_groups.append([i])
        
        processing_time = time.time() - start_time
        self.logger.info(f"Found {len(duplicate_groups)} groups in {processing_time:.2f}s")
        
        # Log group statistics
        multi_item_groups = [g for g in duplicate_groups if len(g) > 1]
        if multi_item_groups:
            self.logger.info(f"Duplicate groups found: {len(multi_item_groups)}")
            for i, group in enumerate(multi_item_groups):
                group_addresses = [addresses[idx] for idx in group]
                self.logger.debug(f"Group {i+1}: {group_addresses}")
        
        return duplicate_groups
    
    def detect_duplicate_pairs(self, addr1: str, addr2: str) -> Dict[str, Any]:
        """
        Compare two addresses for similarity
        
        Args:
            addr1: First address string
            addr2: Second address string
            
        Returns:
            {
                "is_duplicate": bool,
                "similarity_score": float,
                "confidence": float,
                "similarity_breakdown": dict
            }
        """
        try:
            # Get similarity score - use improved basic similarity for better Turkish matching
            basic_similarity = self._calculate_basic_similarity(addr1, addr2)
            
            if self.hybrid_matcher:
                similarity_result = self.hybrid_matcher.calculate_hybrid_similarity(addr1, addr2)
                hybrid_similarity = similarity_result.get('overall_similarity', 0.0)
                breakdown = similarity_result.get('breakdown', {})
                
                # CRITICAL FIX: Apply neighborhood penalty to hybrid similarity as well
                neighborhood_penalty = self._calculate_neighborhood_difference_penalty(addr1, addr2)
                hybrid_similarity_adjusted = max(0.0, hybrid_similarity - neighborhood_penalty)
                
                # Use the higher of the two similarities for Turkish address matching
                similarity_score = max(basic_similarity, hybrid_similarity_adjusted)
                breakdown['basic_turkish'] = basic_similarity
                breakdown['hybrid'] = hybrid_similarity
                breakdown['hybrid_adjusted'] = hybrid_similarity_adjusted
                breakdown['neighborhood_penalty'] = neighborhood_penalty
            else:
                # Fallback: basic string similarity
                similarity_score = basic_similarity
                breakdown = {"textual": similarity_score}
            
            is_duplicate = similarity_score >= self.similarity_threshold
            confidence = min(1.0, similarity_score * 1.2)  # Boost confidence for high similarity
            
            return {
                "is_duplicate": is_duplicate,
                "similarity_score": similarity_score,
                "confidence": confidence,
                "similarity_breakdown": breakdown
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing addresses '{addr1}' and '{addr2}': {e}")
            return {
                "is_duplicate": False,
                "similarity_score": 0.0,
                "confidence": 0.0,
                "similarity_breakdown": {"error": str(e)}
            }
    
    def _build_similarity_matrix(self, addresses: List[str]) -> np.ndarray:
        """Build similarity matrix for all address pairs"""
        n = len(addresses)
        similarity_matrix = np.zeros((n, n))
        
        # Fill diagonal with 1.0 (self-similarity)
        np.fill_diagonal(similarity_matrix, 1.0)
        
        # Calculate upper triangle (symmetric matrix)
        total_comparisons = n * (n - 1) // 2
        completed = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                # Use cache key for optimization
                cache_key = (addresses[i], addresses[j])
                reverse_cache_key = (addresses[j], addresses[i])
                
                if cache_key in self._similarity_cache:
                    similarity = self._similarity_cache[cache_key]
                elif reverse_cache_key in self._similarity_cache:
                    similarity = self._similarity_cache[reverse_cache_key]
                else:
                    # Calculate similarity - use both methods and take the higher score
                    basic_similarity = self._calculate_basic_similarity(addresses[i], addresses[j])
                    
                    if self.hybrid_matcher:
                        similarity_result = self.hybrid_matcher.calculate_hybrid_similarity(addresses[i], addresses[j])
                        hybrid_similarity = similarity_result.get('overall_similarity', 0.0)
                        
                        # CRITICAL FIX: Apply neighborhood penalty to hybrid similarity 
                        neighborhood_penalty = self._calculate_neighborhood_difference_penalty(addresses[i], addresses[j])
                        hybrid_similarity_adjusted = max(0.0, hybrid_similarity - neighborhood_penalty)
                        
                        similarity = max(basic_similarity, hybrid_similarity_adjusted)
                    else:
                        similarity = basic_similarity
                    
                    # Cache result
                    self._similarity_cache[cache_key] = similarity
                
                similarity_matrix[i, j] = similarity
                similarity_matrix[j, i] = similarity  # Symmetric
                
                completed += 1
                if completed % 100 == 0:
                    self.logger.debug(f"Similarity calculations: {completed}/{total_comparisons}")
        
        return similarity_matrix
    
    def _cluster_similar_addresses(self, similarity_matrix: np.ndarray, threshold: float) -> List[List[int]]:
        """
        Cluster addresses based on similarity matrix using connected components approach
        """
        n = similarity_matrix.shape[0]
        visited = [False] * n
        clusters = []
        
        def dfs(node: int, cluster: List[int]):
            """Depth-first search to find connected components"""
            visited[node] = True
            cluster.append(node)
            
            # Find all nodes similar to current node
            for neighbor in range(n):
                if not visited[neighbor] and similarity_matrix[node, neighbor] >= threshold:
                    dfs(neighbor, cluster)
        
        # Find all connected components
        for i in range(n):
            if not visited[i]:
                cluster = []
                dfs(i, cluster)
                if cluster:
                    clusters.append(sorted(cluster))
        
        return clusters
    
    def _calculate_basic_similarity(self, addr1: str, addr2: str) -> float:
        """
        Turkish-aware similarity calculation for addresses with enhanced neighborhood detection
        """
        if not addr1 or not addr2:
            return 0.0
        
        # Normalize addresses for Turkish
        norm_addr1 = self._normalize_turkish_address(addr1.lower().strip())
        norm_addr2 = self._normalize_turkish_address(addr2.lower().strip())
        
        if norm_addr1 == norm_addr2:
            return 1.0
            
        # CRITICAL FIX: Extract and compare neighborhoods explicitly
        neighborhood_penalty = self._calculate_neighborhood_difference_penalty(addr1, addr2)
        
        # Enhanced Turkish abbreviation mappings for complex abbreviation patterns
        abbreviations = {
            # Mahalle variations
            'mahallesi': 'mah', 'mah.': 'mah', 'mah': 'mah', 'mahalle': 'mah',
            'mhl': 'mah', 'mhl.': 'mah',
            
            # Cadde variations  
            'caddesi': 'cd', 'cd.': 'cd', 'cd': 'cd', 'cad': 'cd', 'cad.': 'cd',
            
            # Sokak variations
            'sokak': 'sk', 'sokağı': 'sk', 'sk.': 'sk', 'sk': 'sk', 'sok': 'sk', 'sok.': 'sk',
            
            # Bulvar variations
            'bulvarı': 'blv', 'bulvari': 'blv', 'blv.': 'blv', 'blv': 'blv', 'bulvar': 'blv',
            
            # Number variations
            'no:': 'no', 'no.': 'no', 'numara': 'no', 'numarası': 'no', 'num': 'no', 'num.': 'no',
            
            # Apartment/Daire variations
            'daire': 'daire', 'daire:': 'daire', 'dair': 'daire', 'dair.': 'daire',
            'apartman': 'apt', 'apartmanı': 'apt', 'apt': 'apt', 'apt.': 'apt',
            
            # City abbreviations - critical for test case
            'ankara': 'ankara', 'ank': 'ankara', 'ank.': 'ankara',
            'istanbul': 'istanbul', 'ist': 'istanbul', 'ist.': 'istanbul',
            'izmir': 'izmir', 'izm': 'izmir', 'izm.': 'izmir',
            
            # District abbreviations
            'çankaya': 'cankaya', 'çank': 'cankaya', 'çank.': 'cankaya',
            'kadıköy': 'kadikoy', 'kadik': 'kadikoy', 'kadik.': 'kadikoy',
            'konak': 'konak', 'krnk': 'konak', 'krnk.': 'konak'
        }
        
        # Apply abbreviation normalization with word boundary awareness
        import re
        for full_form, abbrev in abbreviations.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(full_form) + r'\b'
            norm_addr1 = re.sub(pattern, abbrev, norm_addr1)
            norm_addr2 = re.sub(pattern, abbrev, norm_addr2)
        
        # Additional multi-character abbreviation handling for complex cases like "Mh."
        multi_abbrev_patterns = {
            r'\bmh\b\.?': 'mah',
            r'\bcd\b\.?': 'cd', 
            r'\bsk\b\.?': 'sk',
            r'\bblv\b\.?': 'blv',
            r'\bapt\b\.?': 'apt'
        }
        
        for pattern, replacement in multi_abbrev_patterns.items():
            norm_addr1 = re.sub(pattern, replacement, norm_addr1, flags=re.IGNORECASE)
            norm_addr2 = re.sub(pattern, replacement, norm_addr2, flags=re.IGNORECASE)
        
        # Extract key components for comparison
        words1 = set(norm_addr1.split())
        words2 = set(norm_addr2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate component-wise similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # Calculate character-level similarity
        from difflib import SequenceMatcher
        char_similarity = SequenceMatcher(None, norm_addr1, norm_addr2).ratio()
        
        # Calculate position-aware similarity (important words have higher weight)
        important_words = {'istanbul', 'ankara', 'izmir', 'bursa', 'antalya', 'adana', 
                          'kadıköy', 'kadikoy', 'çankaya', 'cankaya', 'konak', 'osmangazi'}
        
        important_matches = 0
        total_important = 0
        for word in words1.union(words2):
            if any(imp_word in word for imp_word in important_words):
                total_important += 1
                if word in words1.intersection(words2):
                    important_matches += 1
        
        important_similarity = important_matches / total_important if total_important > 0 else 0.0
        
        # Combine measures with appropriate weights
        raw_similarity = (
            jaccard_similarity * 0.4 +      # Word overlap
            char_similarity * 0.3 +         # Character similarity  
            important_similarity * 0.3      # Important component matches
        )
        
        # CRITICAL FIX: Apply neighborhood penalty to prevent false duplicates
        final_similarity = max(0.0, raw_similarity - neighborhood_penalty)
        
        return min(1.0, final_similarity)
    
    def _calculate_neighborhood_difference_penalty(self, addr1: str, addr2: str) -> float:
        """
        Calculate penalty for different neighborhoods to prevent false duplicates
        
        This method extracts neighborhood information from both addresses and applies
        a significant penalty if they are clearly different neighborhoods.
        """
        try:
            # Extract neighborhoods using components if available
            if self.parser:
                components1 = self._get_address_components(addr1)
                components2 = self._get_address_components(addr2)
                
                mah1 = components1.get('mahalle', '').lower().strip()
                mah2 = components2.get('mahalle', '').lower().strip()
            else:
                # Fallback: extract neighborhoods using regex patterns
                mah1 = self._extract_neighborhood_fallback(addr1)
                mah2 = self._extract_neighborhood_fallback(addr2)
            
            # If either neighborhood is missing, no penalty (insufficient info)
            if not mah1 or not mah2:
                return 0.0
            
            # Normalize neighborhood names for comparison
            mah1_norm = self._normalize_turkish_text(mah1)
            mah2_norm = self._normalize_turkish_text(mah2)
            
            # If neighborhoods are identical, no penalty
            if mah1_norm == mah2_norm:
                return 0.0
            
            # Check for common neighborhood name variations/abbreviations
            mah1_clean = self._clean_neighborhood_name(mah1_norm)
            mah2_clean = self._clean_neighborhood_name(mah2_norm)
            
            if mah1_clean == mah2_clean:
                return 0.0  # Same neighborhood, different spellings
            
            # Calculate neighborhood similarity to handle minor variations
            neighborhood_similarity = self._calculate_neighborhood_similarity(mah1_clean, mah2_clean)
            
            # If neighborhoods are very similar (>0.8), minimal penalty
            if neighborhood_similarity > 0.8:
                return 0.05  # Small penalty for minor variations
            elif neighborhood_similarity > 0.6:
                return 0.15  # Medium penalty for somewhat similar names
            else:
                # CRITICAL: High penalty for clearly different neighborhoods
                return 0.35  # This will prevent similarity scores >0.75 from becoming duplicates
                
        except Exception as e:
            self.logger.warning(f"Error calculating neighborhood penalty: {e}")
            return 0.0  # No penalty if calculation fails
    
    def _get_address_components(self, address: str) -> dict:
        """Get address components using parser"""
        try:
            result = self.parser.parse_address(address)
            return result.get('components', {})
        except Exception:
            return {}
    
    def _extract_neighborhood_fallback(self, address: str) -> str:
        """Fallback method to extract neighborhood using regex"""
        import re
        address_lower = address.lower()
        
        # Pattern to match "neighborhood + mahalle/mahallesi" 
        patterns = [
            r'(\w+(?:\s+\w+)*)\s+mahallesi',  # "Kızılay Mahallesi"
            r'(\w+(?:\s+\w+)*)\s+mah\b',     # "Kızılay Mah"
            r'(\w+(?:\s+\w+)*)\s+mahalle\b', # "Kızılay Mahalle"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, address_lower)
            if match:
                neighborhood = match.group(1).strip()
                # Filter out common non-neighborhood words
                if neighborhood not in ['sokak', 'sokağı', 'cadde', 'caddesi', 'bulvar', 'bulvarı']:
                    return neighborhood
        
        return ""
    
    def _clean_neighborhood_name(self, neighborhood: str) -> str:
        """Clean and normalize neighborhood name for comparison"""
        # Remove common suffixes that don't affect identity
        cleaned = neighborhood
        suffixes_to_remove = ['sokak', 'sokağı', 'sk', 'mah', 'mahalle', 'mahallesi']
        
        for suffix in suffixes_to_remove:
            if cleaned.endswith(' ' + suffix):
                cleaned = cleaned[:-len(' ' + suffix)].strip()
            elif cleaned == suffix:  # Whole string is suffix
                return ""
        
        return cleaned.strip()
    
    def _calculate_neighborhood_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between neighborhood names"""
        if not name1 or not name2:
            return 0.0
            
        if name1 == name2:
            return 1.0
        
        # Use character-level similarity for neighborhood names
        from difflib import SequenceMatcher
        return SequenceMatcher(None, name1, name2).ratio()
    
    def _normalize_turkish_text(self, text: str) -> str:
        """Normalize Turkish text for comparison"""
        if not text:
            return ""
            
        # Turkish character normalization
        turkish_translation = str.maketrans({
            'İ': 'i', 'ı': 'i', 'I': 'i',
            'ğ': 'g', 'Ğ': 'g',
            'ü': 'u', 'Ü': 'u', 
            'ş': 's', 'Ş': 's',
            'ö': 'o', 'Ö': 'o',
            'ç': 'c', 'Ç': 'c'
        })
        
        normalized = text.lower().translate(turkish_translation)
        
        # Remove extra spaces and punctuation
        import re
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip()
    
    def _normalize_turkish_address(self, address: str) -> str:
        """Normalize Turkish address for better matching with performance optimization"""
        # Check cache first
        if address in self._normalization_cache:
            return self._normalization_cache[address]
        
        # Turkish character normalization - use proper single character mapping
        turkish_translation = str.maketrans({
            'İ': 'i', 'ı': 'i', 'I': 'i',
            'ğ': 'g', 'Ğ': 'g',
            'ü': 'u', 'Ü': 'u', 
            'ş': 's', 'Ş': 's',
            'ö': 'o', 'Ö': 'o',
            'ç': 'c', 'Ç': 'c'
        })
        
        normalized = address.translate(turkish_translation)
            
        # Remove extra spaces and punctuation - compile regex once for performance
        import re
        if not hasattr(self, '_punct_regex'):
            self._punct_regex = re.compile(r'[^\w\s]')
            self._space_regex = re.compile(r'\s+')
        
        normalized = self._punct_regex.sub(' ', normalized)  # Replace punctuation with spaces
        normalized = self._space_regex.sub(' ', normalized)  # Collapse multiple spaces
        
        result = normalized.strip()
        
        # Cache the result
        self._normalization_cache[address] = result
        return result
    
    def get_duplicate_statistics(self, addresses: List[str]) -> Dict[str, Any]:
        """
        Get detailed statistics about duplicates in address list
        
        Args:
            addresses: List of addresses to analyze
            
        Returns:
            Dictionary with duplicate statistics
        """
        if not addresses:
            return {
                "total_addresses": 0,
                "duplicate_groups": 0,
                "total_duplicates": 0,
                "unique_addresses": 0,
                "duplication_rate": 0.0
            }
        
        groups = self.find_duplicate_groups(addresses)
        
        duplicate_groups = [group for group in groups if len(group) > 1]
        total_duplicates = sum(len(group) - 1 for group in duplicate_groups)  # Don't count the "original" in each group
        unique_addresses = len(groups)  # Each group represents one unique address
        
        stats = {
            "total_addresses": len(addresses),
            "duplicate_groups": len(duplicate_groups),
            "total_duplicates": total_duplicates,
            "unique_addresses": unique_addresses,
            "duplication_rate": total_duplicates / len(addresses) if addresses else 0.0,
            "largest_duplicate_group": max(len(group) for group in duplicate_groups) if duplicate_groups else 0,
            "groups": groups
        }
        
        return stats
    
    def deduplicate_addresses(self, addresses: List[str]) -> Tuple[List[str], List[List[int]]]:
        """
        Remove duplicates from address list, keeping one representative from each group
        
        Args:
            addresses: List of addresses with potential duplicates
            
        Returns:
            Tuple of (unique_addresses, original_groups)
        """
        if not addresses:
            return [], []
        
        groups = self.find_duplicate_groups(addresses)
        unique_addresses = []
        
        for group in groups:
            # Keep the first address from each group as representative
            representative_idx = group[0]
            unique_addresses.append(addresses[representative_idx])
        
        self.logger.info(f"Deduplicated {len(addresses)} addresses to {len(unique_addresses)} unique addresses")
        
        return unique_addresses, groups
    
    def batch_duplicate_detection(self, address_batches: List[List[str]], batch_size: int = 1000) -> List[List[List[int]]]:
        """
        Efficiently process large datasets in batches
        
        Args:
            address_batches: List of address batches
            batch_size: Maximum size for each batch
            
        Returns:
            List of duplicate groups for each batch
        """
        results = []
        
        for i, batch in enumerate(address_batches):
            self.logger.info(f"Processing batch {i+1}/{len(address_batches)} ({len(batch)} addresses)")
            
            try:
                batch_groups = self.find_duplicate_groups(batch)
                results.append(batch_groups)
            except Exception as e:
                self.logger.error(f"Error processing batch {i+1}: {e}")
                # Return individual groups as fallback
                fallback_groups = [[j] for j in range(len(batch))]
                results.append(fallback_groups)
        
        return results


# Test function for TEKNOFEST validation
def test_duplicate_detector():
    """Test duplicate detection with Turkish addresses"""
    print("🔍 TESTING DUPLICATE ADDRESS DETECTION")
    print("=" * 50)
    
    detector = DuplicateAddressDetector(similarity_threshold=0.85)
    
    # Test addresses with known duplicates
    test_addresses = [
        "Istanbul Kadıköy Moda Mahallesi Caferağa Sokak 10",
        "İstanbul Kadıköy Moda Mah. Caferağa Sk. 10",  # Same as #1
        "Ankara Çankaya Tunalı Hilmi Caddesi 25",
        "Ankara Çankaya Tunali Hilmi Cd. 25",  # Same as #3
        "İzmir Konak Alsancak Mahallesi",
        "Bursa Osmangazi Heykel Mahallesi",
        "İstanbul Kadıköy Moda Caferağa 10",  # Similar to #1
        "Izmir Konak Alsancak Mah.",  # Same as #5
    ]
    
    print(f"Testing with {len(test_addresses)} addresses:")
    for i, addr in enumerate(test_addresses):
        print(f"  {i}: {addr}")
    
    # Find duplicate groups
    groups = detector.find_duplicate_groups(test_addresses)
    
    print(f"\nFound {len(groups)} groups:")
    for i, group in enumerate(groups):
        if len(group) > 1:
            print(f"  Duplicate Group {i+1}: {group}")
            for idx in group:
                print(f"    - {test_addresses[idx]}")
        else:
            print(f"  Unique: {group[0]} - {test_addresses[group[0]]}")
    
    # Test pair comparison
    print(f"\nPair comparison test:")
    addr1 = test_addresses[0]
    addr2 = test_addresses[1]
    result = detector.detect_duplicate_pairs(addr1, addr2)
    print(f"  Address 1: {addr1}")
    print(f"  Address 2: {addr2}")
    print(f"  Is duplicate: {result['is_duplicate']}")
    print(f"  Similarity: {result['similarity_score']:.3f}")
    print(f"  Confidence: {result['confidence']:.3f}")
    
    # Get statistics
    stats = detector.get_duplicate_statistics(test_addresses)
    print(f"\nDuplicate Statistics:")
    print(f"  Total addresses: {stats['total_addresses']}")
    print(f"  Duplicate groups: {stats['duplicate_groups']}")
    print(f"  Total duplicates: {stats['total_duplicates']}")
    print(f"  Unique addresses: {stats['unique_addresses']}")
    print(f"  Duplication rate: {stats['duplication_rate']:.1%}")
    
    print("\n✅ Duplicate detection test completed!")
    return groups, stats


if __name__ == "__main__":
    test_duplicate_detector()