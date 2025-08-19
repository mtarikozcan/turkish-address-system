#!/usr/bin/env python3
"""
TEKNOFEST KAGGLE YARIŞMASI ÇÖZÜMÜ - OPTİMİZE VERSİYON
Hızlı ve etkili adres eşleştirme çözümü
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import re
from collections import Counter

class TeknoFestOptimizedSolution:
    """Optimize edilmiş yarışma çözümü"""
    
    def __init__(self):
        """Hızlı başlatma"""
        print("🚀 OPTİMİZE ÇÖZÜM BAŞLATILIYOR...")
        self.setup_mappings()
        
    def setup_mappings(self):
        """Temel mapping'ler"""
        # Kısaltma genişletmeleri
        self.abbreviations = {
            'mah.': 'mahallesi', 'mah': 'mahallesi',
            'cd.': 'caddesi', 'cad.': 'caddesi', 'cad': 'caddesi',
            'sk.': 'sokağı', 'sok.': 'sokağı', 'sok': 'sokağı',
            'blv.': 'bulvarı', 'bul.': 'bulvarı',
            'no:': 'no:', 'no.': 'no:'
        }
        
        # Şehir listesi
        self.cities = ['istanbul', 'ankara', 'izmir', 'bursa', 'antalya', 'adana', 'konya']
        
        # İlçe listesi (kısaltılmış)
        self.districts = {
            'istanbul': ['kadıköy', 'beşiktaş', 'şişli', 'beyoğlu', 'fatih', 'üsküdar', 
                        'bakırköy', 'zeytinburnu', 'maltepe', 'kartal', 'pendik'],
            'ankara': ['çankaya', 'keçiören', 'yenimahalle', 'etimesgut', 'sincan',
                      'altındağ', 'mamak', 'pursaklar', 'gölbaşı'],
            'izmir': ['konak', 'karşıyaka', 'bornova', 'buca', 'çiğli', 'gaziemir'],
            'bursa': ['osmangazi', 'nilüfer', 'yıldırım', 'mudanya', 'gemlik'],
            'antalya': ['muratpaşa', 'konyaaltı', 'kepez', 'döşemealtı', 'aksu'],
            'adana': ['seyhan', 'yüreğir', 'çukurova', 'sarıçam'],
            'konya': ['meram', 'selçuklu', 'karatay']
        }
    
    def quick_normalize(self, text: str) -> str:
        """Hızlı normalizasyon"""
        normalized = text.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Kısaltmaları genişlet
        for abbr, full in self.abbreviations.items():
            normalized = normalized.replace(abbr, full)
        
        # Noktalama temizliği
        normalized = normalized.replace(',', ' ').replace('.', ' ')
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def extract_key_components(self, address: str) -> Dict:
        """Kritik bileşenleri hızlıca çıkar"""
        normalized = self.quick_normalize(address)
        components = {}
        
        # Şehir bul
        for city in self.cities:
            if city in normalized:
                components['il'] = city
                
                # Bu şehrin ilçelerini kontrol et
                if city in self.districts:
                    for district in self.districts[city]:
                        if district in normalized:
                            components['ilce'] = district
                            break
                break
        
        # Mahalle bul
        mahalle_match = re.search(r'(\w+)\s+mahallesi', normalized)
        if mahalle_match:
            components['mahalle'] = mahalle_match.group(1)
        
        # Numara bul
        no_match = re.search(r'no:\s*(\d+)', normalized)
        if no_match:
            components['no'] = no_match.group(1)
        
        return components
    
    def create_location_signature(self, components: Dict) -> str:
        """Lokasyon imzası oluştur"""
        parts = []
        for key in ['il', 'ilce', 'mahalle', 'no']:
            if key in components:
                parts.append(components[key])
        return '_'.join(parts) if parts else 'unknown'
    
    def solve_fast(self, train_path: str, test_path: str, output_path: str):
        """Hızlı çözüm"""
        print("\n🏁 HIZLI ÇÖZÜM BAŞLIYOR...")
        
        # Veri yükle
        print("📊 Veriler yükleniyor...")
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
        
        print(f"✅ Train: {len(train_df):,} örnek")
        print(f"✅ Test: {len(test_df):,} örnek")
        
        # STRATEJİ 1: Koordinat + Basit Adres Benzerliği
        print("\n🔍 Strateji 1: Koordinat bazlı gruplandırma...")
        
        # Train verisinden lokasyon imzası -> target_id mapping oluştur
        location_to_target = {}
        target_frequency = Counter()
        
        for _, row in train_df.iterrows():
            components = self.extract_key_components(row['address_text'])
            signature = self.create_location_signature(components)
            
            if signature != 'unknown':
                if signature not in location_to_target:
                    location_to_target[signature] = []
                location_to_target[signature].append(row['target_id'])
                target_frequency[row['target_id']] += 1
        
        print(f"✅ {len(location_to_target):,} unique lokasyon imzası oluşturuldu")
        
        # En sık kullanılan target_id (fallback için)
        most_common_target = target_frequency.most_common(1)[0][0]
        
        # Test verilerini tahmin et
        predictions = []
        
        for _, test_row in test_df.iterrows():
            test_id = test_row['id']
            test_addr = test_row['address_text']
            test_lat = test_row['latitude']
            test_lon = test_row['longitude']
            
            # Test adresinden imza oluştur
            test_components = self.extract_key_components(test_addr)
            test_signature = self.create_location_signature(test_components)
            
            # İmza eşleşmesi var mı?
            if test_signature in location_to_target:
                # Bu imzaya ait target_id'lerden en sık olanı seç
                candidates = location_to_target[test_signature]
                target_counts = Counter(candidates)
                best_target = target_counts.most_common(1)[0][0]
            else:
                # STRATEJİ 2: En yakın koordinat
                # Basit mesafe hesabı
                train_df['distance'] = ((train_df['latitude'] - test_lat)**2 + 
                                       (train_df['longitude'] - test_lon)**2)**0.5
                
                # En yakın 5 noktayı al
                nearest = train_df.nsmallest(5, 'distance')
                
                # En yakın noktaların target_id'lerinden en sık olanı
                nearest_targets = nearest['target_id'].value_counts()
                if len(nearest_targets) > 0:
                    best_target = nearest_targets.index[0]
                else:
                    best_target = most_common_target
            
            predictions.append({
                'id': test_id,
                'target_id': best_target
            })
        
        # Submission oluştur
        submission_df = pd.DataFrame(predictions)
        submission_df = submission_df.sort_values('id')
        submission_df.to_csv(output_path, index=False)
        
        print(f"\n✅ Submission oluşturuldu: {output_path}")
        print(f"📊 {len(submission_df):,} tahmin yapıldı")
        print(f"🎯 {submission_df['target_id'].nunique():,} unique target_id kullanıldı")
        
        # İstatistikler
        print("\n📈 TAHMİN İSTATİSTİKLERİ:")
        print(f"En sık tahmin: {submission_df['target_id'].value_counts().index[0]} " +
              f"({submission_df['target_id'].value_counts().values[0]} kez)")
        
        # Örnek tahminler
        print("\n📋 ÖRNEK TAHMİNLER:")
        for i in range(min(3, len(submission_df))):
            row = submission_df.iloc[i]
            test_addr = test_df[test_df['id'] == row['id']]['address_text'].values[0]
            print(f"ID {row['id']}: '{test_addr[:60]}...'")
            print(f"         → Target: {row['target_id']}")
        
        return submission_df

def main():
    """Ana çözüm"""
    print("🏆 TEKNOFEST KAGGLE YARIŞMASI - OPTİMİZE ÇÖZÜM")
    print("=" * 70)
    
    # Çözümü başlat
    solution = TeknoFestOptimizedSolution()
    
    # Veri yolları
    data_dir = "/Users/tarikozcan/Desktop/adres_hackhaton/kaggle_data"
    train_path = f"{data_dir}/train.csv"
    test_path = f"{data_dir}/test.csv"
    output_path = f"{data_dir}/submission_optimized.csv"
    
    # Çözümü çalıştır
    submission_df = solution.solve_fast(train_path, test_path, output_path)
    
    print("\n🚀 OPTİMİZE ÇÖZÜM TAMAMLANDI!")
    print("Submission dosyası: submission_optimized.csv")
    print("Simülatörde test etmeye hazır!")
    
    return output_path

if __name__ == "__main__":
    submission_path = main()