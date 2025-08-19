#!/usr/bin/env python3
"""
TEKNOFEST KAGGLE YARIŞMASI ÇÖZÜMÜ
Mevcut Turkish Address Processing System kullanarak adres eşleştirme
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import re
from typing import Dict, List, Tuple
import json

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

class TeknoFestAddressSolution:
    """TEKNOFEST Adres Çözümleme Yarışması Çözümü"""
    
    def __init__(self):
        """Mevcut modelleri yükle"""
        print("🚀 TEKNOFEST ÇÖZÜMÜ BAŞLATILIYOR...")
        
        # Mevcut Turkish Address Parser'ı yükle
        try:
            from address_parser import AddressParser
            self.parser = AddressParser()
            print("✅ Address Parser yüklendi")
        except:
            print("⚠️ Address Parser yüklenemedi, basit parser kullanılacak")
            self.parser = None
        
        # Turkish admin hierarchy verisini yükle (55K kayıt)
        self.load_turkish_admin_data()
        
        # Temizleme ve normalize etme için mapping'ler
        self.setup_normalization_mappings()
        
    def load_turkish_admin_data(self):
        """55K'lık Turkish admin hierarchy verisini yükle"""
        try:
            admin_path = current_dir / "data" / "turkey_admin_hierarchy.csv"
            self.admin_df = pd.read_csv(admin_path, encoding='utf-8')
            print(f"✅ Turkish admin verisi yüklendi: {len(self.admin_df):,} kayıt")
            
            # İndeks oluştur hızlı arama için
            self.create_location_indices()
        except Exception as e:
            print(f"⚠️ Admin verisi yüklenemedi: {e}")
            self.admin_df = None
    
    def create_location_indices(self):
        """Hızlı arama için lokasyon indeksleri oluştur"""
        if self.admin_df is not None:
            # İl-İlçe-Mahalle kombinasyonları
            self.location_index = {}
            for _, row in self.admin_df.iterrows():
                key = f"{row['il']}_{row['ilce']}_{row['mahalle']}".lower()
                self.location_index[key] = {
                    'il': row['il'],
                    'ilce': row['ilce'], 
                    'mahalle': row['mahalle']
                }
            print(f"✅ Lokasyon indeksi oluşturuldu: {len(self.location_index):,} kombinasyon")
    
    def setup_normalization_mappings(self):
        """Adres normalizasyon mapping'leri"""
        # Kısaltma genişletmeleri
        self.abbreviation_map = {
            'mah.': 'mahallesi',
            'mah': 'mahallesi',
            'cd.': 'caddesi',
            'cd': 'caddesi',
            'cad.': 'caddesi',
            'cad': 'caddesi',
            'sk.': 'sokağı',
            'sk': 'sokağı',
            'sok.': 'sokağı',
            'sok': 'sokağı',
            'blv.': 'bulvarı',
            'blv': 'bulvarı',
            'bul.': 'bulvarı',
            'bul': 'bulvarı',
            'apt.': 'apartmanı',
            'apt': 'apartmanı',
            'no:': 'no:',
            'no.': 'no:',
            'kat:': 'kat:',
            'd:': 'daire:'
        }
        
        # Türkçe karakter mapping'i
        self.turkish_char_map = {
            'i': 'ı', 'ı': 'i',
            'g': 'ğ', 'ğ': 'g',
            's': 'ş', 'ş': 's',
            'c': 'ç', 'ç': 'c',
            'u': 'ü', 'ü': 'u',
            'o': 'ö', 'ö': 'o'
        }
    
    def normalize_address(self, address: str) -> str:
        """Adresi normalize et"""
        # Küçük harfe çevir
        normalized = address.lower().strip()
        
        # Fazla boşlukları temizle
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Kısaltmaları genişlet
        for abbr, full in self.abbreviation_map.items():
            normalized = re.sub(r'\b' + re.escape(abbr) + r'\b', full, normalized)
        
        # Noktalama temizliği
        normalized = normalized.replace(',', ' ').replace('.', ' ')
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def extract_components(self, address: str) -> Dict:
        """Adresten bileşenleri çıkar"""
        components = {}
        normalized = self.normalize_address(address)
        
        # Parse with existing parser if available
        if self.parser:
            try:
                result = self.parser.parse_address(address)
                if result and 'components' in result:
                    return result['components']
            except:
                pass
        
        # Fallback: Basit pattern matching
        patterns = {
            'il': r'\b(istanbul|ankara|izmir|bursa|antalya|adana|konya)\b',
            'ilce': r'\b(kadıköy|beşiktaş|şişli|çankaya|keçiören|konak|karşıyaka|nilüfer|muratpaşa|seyhan|meram|selçuklu)\b',
            'mahalle': r'(\w+)\s+mahallesi',
            'cadde': r'(\w+)\s+caddesi',
            'sokak': r'(\w+)\s+sokağı',
            'no': r'no:\s*(\d+)',
            'daire': r'daire:\s*(\d+)'
        }
        
        for comp_name, pattern in patterns.items():
            match = re.search(pattern, normalized)
            if match:
                components[comp_name] = match.group(1) if comp_name not in ['il', 'ilce'] else match.group(0)
        
        return components
    
    def calculate_similarity_score(self, addr1_components: Dict, addr2_components: Dict) -> float:
        """İki adres arasındaki benzerlik skoru hesapla"""
        score = 0.0
        weights = {
            'il': 0.3,
            'ilce': 0.25,
            'mahalle': 0.2,
            'cadde': 0.1,
            'sokak': 0.1,
            'no': 0.05
        }
        
        for comp, weight in weights.items():
            if comp in addr1_components and comp in addr2_components:
                if addr1_components[comp].lower() == addr2_components[comp].lower():
                    score += weight
        
        return score
    
    def find_matching_addresses(self, test_address: str, train_addresses: List[Tuple[str, str]]) -> str:
        """Test adresine en uygun train adresini bul"""
        test_components = self.extract_components(test_address)
        
        if not test_components:
            # Bileşen çıkarılamazsa en yakın string benzerliğini kullan
            return self.find_by_string_similarity(test_address, train_addresses)
        
        best_match = None
        best_score = 0.0
        
        for train_addr, target_id in train_addresses:
            train_components = self.extract_components(train_addr)
            
            if not train_components:
                continue
            
            similarity = self.calculate_similarity_score(test_components, train_components)
            
            if similarity > best_score:
                best_score = similarity
                best_match = target_id
        
        # Eğer hiç eşleşme bulunamazsa, en sık kullanılan target_id'yi döndür
        if best_match is None:
            target_counts = {}
            for _, target_id in train_addresses:
                target_counts[target_id] = target_counts.get(target_id, 0) + 1
            best_match = max(target_counts, key=target_counts.get)
        
        return best_match
    
    def find_by_string_similarity(self, test_addr: str, train_addresses: List[Tuple[str, str]]) -> str:
        """Basit string benzerliği ile eşleştir"""
        test_normalized = self.normalize_address(test_addr)
        
        best_match = None
        best_score = 0
        
        for train_addr, target_id in train_addresses:
            train_normalized = self.normalize_address(train_addr)
            
            # Basit Jaccard similarity
            test_words = set(test_normalized.split())
            train_words = set(train_normalized.split())
            
            if len(test_words.union(train_words)) > 0:
                similarity = len(test_words.intersection(train_words)) / len(test_words.union(train_words))
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = target_id
        
        if best_match is None:
            # Fallback: İlk target_id
            best_match = train_addresses[0][1] if train_addresses else "unknown"
        
        return best_match
    
    def use_coordinate_clustering(self, test_df: pd.DataFrame, train_df: pd.DataFrame) -> Dict[int, str]:
        """Koordinat bazlı kümeleme ile eşleştirme"""
        predictions = {}
        
        # Her test noktası için en yakın train noktalarını bul
        for _, test_row in test_df.iterrows():
            test_lat = test_row['latitude']
            test_lon = test_row['longitude']
            test_id = test_row['id']
            
            # Mesafe hesapla (basit Euclidean)
            train_df['distance'] = np.sqrt(
                (train_df['latitude'] - test_lat)**2 + 
                (train_df['longitude'] - test_lon)**2
            )
            
            # En yakın 10 noktayı al
            nearest = train_df.nsmallest(10, 'distance')
            
            # En yakın noktaların adreslerini karşılaştır
            test_addr = test_row['address_text']
            train_addresses = [(row['address_text'], row['target_id']) for _, row in nearest.iterrows()]
            
            # En iyi eşleşmeyi bul
            best_target = self.find_matching_addresses(test_addr, train_addresses)
            predictions[test_id] = best_target
        
        return predictions
    
    def solve_competition(self, train_path: str, test_path: str, output_path: str):
        """Ana çözüm metodu"""
        print("\n🏁 YARIŞMA ÇÖZÜMÜ BAŞLIYOR...")
        
        # Veri yükle
        print("📊 Veriler yükleniyor...")
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
        
        print(f"✅ Train: {len(train_df):,} örnek")
        print(f"✅ Test: {len(test_df):,} örnek")
        print(f"✅ Unique target: {train_df['target_id'].nunique():,}")
        
        # Strateji 1: Koordinat bazlı kümeleme + Adres benzerliği
        print("\n🔍 Koordinat ve adres benzerliği ile eşleştirme...")
        predictions = self.use_coordinate_clustering(test_df, train_df)
        
        # Strateji 2: Temiz adreslerden öğrenme (train'de var)
        print("🧠 Temiz adres pattern'lerinden öğrenme...")
        
        # Clean address'lerden pattern çıkar
        clean_patterns = {}
        for _, row in train_df.iterrows():
            clean_normalized = self.normalize_address(row['clean_address'])
            components = self.extract_components(clean_normalized)
            
            # Pattern oluştur
            if 'il' in components and 'ilce' in components:
                pattern_key = f"{components.get('il', '')}_{components.get('ilce', '')}".lower()
                if pattern_key not in clean_patterns:
                    clean_patterns[pattern_key] = []
                clean_patterns[pattern_key].append(row['target_id'])
        
        # Test verilerini pattern'lerle eşleştir
        improved_predictions = {}
        for _, test_row in test_df.iterrows():
            test_id = test_row['id']
            test_addr = test_row['address_text']
            
            # Test adresinden component çıkar
            test_components = self.extract_components(test_addr)
            
            if 'il' in test_components and 'ilce' in test_components:
                pattern_key = f"{test_components.get('il', '')}_{test_components.get('ilce', '')}".lower()
                
                if pattern_key in clean_patterns:
                    # Bu pattern'e ait target_id'lerden en sık olanı seç
                    target_candidates = clean_patterns[pattern_key]
                    target_counts = {}
                    for tid in target_candidates:
                        target_counts[tid] = target_counts.get(tid, 0) + 1
                    
                    best_target = max(target_counts, key=target_counts.get)
                    improved_predictions[test_id] = best_target
                else:
                    # Fallback to original prediction
                    improved_predictions[test_id] = predictions.get(test_id, train_df.iloc[0]['target_id'])
            else:
                improved_predictions[test_id] = predictions.get(test_id, train_df.iloc[0]['target_id'])
        
        # Submission oluştur
        submission_df = pd.DataFrame([
            {'id': test_id, 'target_id': target_id}
            for test_id, target_id in improved_predictions.items()
        ])
        
        submission_df = submission_df.sort_values('id')
        submission_df.to_csv(output_path, index=False)
        
        print(f"\n✅ Submission oluşturuldu: {output_path}")
        print(f"📊 {len(submission_df):,} tahmin yapıldı")
        print(f"🎯 {submission_df['target_id'].nunique():,} unique target_id kullanıldı")
        
        # Örnek tahminler
        print("\n📋 ÖRNEK TAHMİNLER:")
        for i in range(min(5, len(submission_df))):
            row = submission_df.iloc[i]
            test_addr = test_df[test_df['id'] == row['id']]['address_text'].values[0]
            print(f"ID {row['id']}: '{test_addr[:50]}...' → Target: {row['target_id']}")
        
        return submission_df

def main():
    """Ana çözüm çalıştırıcı"""
    print("🏆 TEKNOFEST ADRES ÇÖZÜMLEME YARIŞMASI")
    print("=" * 70)
    print("Turkish Address Processing System ile Çözüm")
    
    # Çözümü başlat
    solution = TeknoFestAddressSolution()
    
    # Veri yolları
    data_dir = "/Users/tarikozcan/Desktop/adres_hackhaton/kaggle_data"
    train_path = f"{data_dir}/train.csv"
    test_path = f"{data_dir}/test.csv"
    output_path = f"{data_dir}/submission.csv"
    
    # Çözümü çalıştır
    submission_df = solution.solve_competition(train_path, test_path, output_path)
    
    print("\n🚀 ÇÖZÜM TAMAMLANDI!")
    print("Submission dosyası hazır: submission.csv")
    print("Simülatörde test etmek için hazır!")
    
    return output_path

if __name__ == "__main__":
    submission_path = main()