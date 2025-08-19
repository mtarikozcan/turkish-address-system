#!/usr/bin/env python3
"""
TEKNOFEST YAPAY ZEKA DESTEKLİ ADRES ÇÖZÜMLEME YARIŞMASI
Kaggle Aşaması Simülatörü
Gerçekçi sentetik Türkçe adres veri seti üretimi
"""

import pandas as pd
import numpy as np
import random
import uuid
import json
from typing import List, Dict, Tuple
import os

# Sabit tohum değeri - tekrarlanabilir sonuçlar için
np.random.seed(42)
random.seed(42)

class TeknoFestAddressDataGenerator:
    """Gerçekçi sentetik Türkçe adres veri seti üreticisi"""
    
    def __init__(self):
        """Türkiye'nin gerçek coğrafi verilerini başlat"""
        
        # Ana şehirler ve koordinatları (gerçek)
        self.cities = {
            'İstanbul': {'lat': 41.0082, 'lon': 28.9784, 'districts': [
                'Kadıköy', 'Beşiktaş', 'Şişli', 'Beyoğlu', 'Fatih', 'Üsküdar', 
                'Bakırköy', 'Zeytinburnu', 'Maltepe', 'Kartal', 'Pendik'
            ]},
            'Ankara': {'lat': 39.9334, 'lon': 32.8597, 'districts': [
                'Çankaya', 'Keçiören', 'Yenimahalle', 'Etimesgut', 'Sincan',
                'Altındağ', 'Mamak', 'Pursaklar', 'Gölbaşı'
            ]},
            'İzmir': {'lat': 38.4192, 'lon': 27.1287, 'districts': [
                'Konak', 'Karşıyaka', 'Bornova', 'Buca', 'Çiğli', 
                'Gaziemir', 'Balçova', 'Narlıdere', 'Bayraklı'
            ]},
            'Bursa': {'lat': 40.1826, 'lon': 29.0669, 'districts': [
                'Osmangazi', 'Nilüfer', 'Yıldırım', 'Mudanya', 'Gemlik',
                'İnegöl', 'Mustafakemalpaşa', 'Orhaneli'
            ]},
            'Antalya': {'lat': 36.8969, 'lon': 30.7133, 'districts': [
                'Muratpaşa', 'Konyaaltı', 'Kepez', 'Döşemealtı', 'Aksu',
                'Serik', 'Manavgat', 'Alanya', 'Side'
            ]},
            'Adana': {'lat': 37.0000, 'lon': 35.3213, 'districts': [
                'Seyhan', 'Yüreğir', 'Çukurova', 'Sarıçam', 'Karaisalı',
                'Pozantı', 'Feke', 'Tufanbeyli'
            ]},
            'Konya': {'lat': 37.8713, 'lon': 32.4846, 'districts': [
                'Meram', 'Selçuklu', 'Karatay', 'Ereğli', 'Akşehir',
                'Beyşehir', 'Seydişehir', 'Cihanbeyli'
            ]}
        }
        
        # Mahalle isimleri (gerçekçi örnekler)
        self.neighborhoods = [
            'Merkez', 'Yeni', 'Cumhuriyet', 'Atatürk', 'Fatih', 'Mehmet Akif',
            'İnönü', 'Gazi', 'Sakarya', 'Mimar Sinan', 'Barbaros', 'Alparslan',
            'Şehitler', 'Yeşiltepe', 'Güneşli', 'Çamlıca', 'Bağlar', 'Çiçek',
            'Bahçelievler', 'Emek', 'Kültür', 'Esentepe', 'Kızılay', 'Çankaya',
            'Etlik', 'Keçiören', 'Yenişehir', 'Eskişehir', 'Mecidiyeköy', 
            'Levent', 'Nişantaşı', 'Taksim', 'Beşiktaş', 'Ortaköy', 'Maslak',
            'Alsancak', 'Konak', 'Karşıyaka', 'Bornova', 'Çiğli', 'Gaziemir'
        ]
        
        # Sokak/Cadde isimleri 
        self.street_names = [
            'Atatürk', 'İnönü', 'Cumhuriyet', 'Gazi', 'Barbaros', 'Fatih',
            'Mehmet Akif', 'Mimar Sinan', 'Sakarya', 'İstiklal', 'Hürriyet',
            'Adalet', 'Barış', 'Dostluk', 'Kardeşlik', 'Güzelyalı', 'Kordon',
            'Büyükdere', 'Bağdat', 'İstiklal', 'Abdi İpekçi', 'Teşvikiye',
            '1. Sok', '2. Sok', '15. Sok', '23. Sok', '45. Sok', '67. Sok',
            'Çamlık', 'Gülistan', 'Yeşillik', 'Çiçekli', 'Güllü'
        ]
        
        # Sokak türleri ve kısaltmaları
        self.street_types = [
            {'full': 'Caddesi', 'abbrev': 'Cd.'}, 
            {'full': 'Sokağı', 'abbrev': 'Sk.'}, 
            {'full': 'Bulvarı', 'abbrev': 'Blv.'}, 
            {'full': 'Sokak', 'abbrev': 'Sk'},
            {'full': 'Cadde', 'abbrev': 'Cad'},
            {'full': 'Bulvar', 'abbrev': 'Bul'}
        ]
    
    def generate_coordinate_variation(self, base_lat: float, base_lon: float, 
                                    radius_km: float = 5.0) -> Tuple[float, float]:
        """Bir noktanın etrafında rastgele koordinat üret"""
        # 1 km ≈ 0.009 derece (yaklaşık)
        lat_variation = np.random.uniform(-radius_km * 0.009, radius_km * 0.009)
        lon_variation = np.random.uniform(-radius_km * 0.009, radius_km * 0.009)
        
        return (
            round(base_lat + lat_variation, 6),
            round(base_lon + lon_variation, 6)
        )
    
    def generate_clean_address(self) -> Dict:
        """Temiz, standardize edilmiş adres üret"""
        # Şehir seç
        city = random.choice(list(self.cities.keys()))
        city_data = self.cities[city]
        
        # İlçe seç
        district = random.choice(city_data['districts'])
        
        # Mahalle seç
        neighborhood = random.choice(self.neighborhoods)
        
        # Sokak bilgisi
        street_name = random.choice(self.street_names)
        street_type = random.choice(self.street_types)
        
        # Kapı numarası
        building_no = random.randint(1, 999)
        
        # Daire numarası (bazen)
        apartment_no = None
        if random.random() < 0.3:  # %30 olasılık
            apartment_no = random.randint(1, 50)
        
        # Koordinat üret
        lat, lon = self.generate_coordinate_variation(
            city_data['lat'], city_data['lon'], radius_km=8.0
        )
        
        # Temiz adres formatı
        address_parts = []
        address_parts.append(f"{neighborhood} Mahallesi")
        address_parts.append(f"{street_name} {street_type['full']}")
        
        if apartment_no:
            address_parts.append(f"No: {building_no}/{apartment_no}")
        else:
            address_parts.append(f"No: {building_no}")
            
        address_parts.append(district)
        address_parts.append(city)
        
        clean_address = ", ".join(address_parts)
        
        return {
            'clean_address': clean_address,
            'city': city,
            'district': district, 
            'neighborhood': neighborhood,
            'street_name': street_name,
            'street_type': street_type['full'],
            'building_no': building_no,
            'apartment_no': apartment_no,
            'latitude': lat,
            'longitude': lon
        }
    
    def corrupt_address(self, clean_data: Dict) -> str:
        """Temiz adresi gerçekçi şekilde boz (yazım hataları, eksiklikler, etc.)"""
        corruption_functions = [
            self._add_typos,
            self._abbreviate_randomly, 
            self._remove_components,
            self._change_order,
            self._add_extra_spaces,
            self._remove_punctuation,
            self._mix_case,
            self._add_noise_words
        ]
        
        # Temiz adresten başla
        corrupted = clean_data['clean_address']
        
        # 1-3 arası bozma işlemi uygula
        num_corruptions = random.randint(1, 3)
        applied_corruptions = random.sample(corruption_functions, num_corruptions)
        
        for corruption_func in applied_corruptions:
            corrupted = corruption_func(corrupted, clean_data)
        
        return corrupted
    
    def _add_typos(self, address: str, clean_data: Dict) -> str:
        """Yazım hataları ekle"""
        typo_map = {
            'ı': 'i', 'i': 'ı', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ü': 'u', 'ö': 'o',
            'İ': 'I', 'I': 'i', 'Ğ': 'G', 'Ş': 'S', 'Ç': 'C', 'Ü': 'U', 'Ö': 'O'
        }
        
        result = ""
        for char in address:
            if char in typo_map and random.random() < 0.1:  # %10 olasılık
                result += typo_map[char]
            else:
                result += char
        return result
    
    def _abbreviate_randomly(self, address: str, clean_data: Dict) -> str:
        """Rastgele kısaltmalar"""
        abbreviations = {
            'Mahallesi': 'Mah.', 'Caddesi': 'Cd.', 'Sokağı': 'Sk.',
            'Bulvarı': 'Blv.', 'Cadde': 'Cad', 'Sokak': 'Sk',
            'Bulvar': 'Blv', 'Mahalle': 'Mah'
        }
        
        for full_form, abbrev in abbreviations.items():
            if random.random() < 0.4:  # %40 olasılık
                address = address.replace(full_form, abbrev)
        
        return address
    
    def _remove_components(self, address: str, clean_data: Dict) -> str:
        """Bazı bileşenleri eksilt"""
        components = address.split(', ')
        
        if len(components) > 3 and random.random() < 0.3:
            # %30 olasılıkla bir bileşen çıkar
            remove_idx = random.randint(0, len(components) - 2)  # Son şehri çıkarma
            components.pop(remove_idx)
        
        return ', '.join(components)
    
    def _change_order(self, address: str, clean_data: Dict) -> str:
        """Bileşenlerin sırasını değiştir"""
        components = address.split(', ')
        
        if len(components) >= 3 and random.random() < 0.2:
            # İlk iki bileşenin yerini değiştir
            components[0], components[1] = components[1], components[0]
        
        return ', '.join(components)
    
    def _add_extra_spaces(self, address: str, clean_data: Dict) -> str:
        """Fazla boşluklar ekle"""
        if random.random() < 0.3:
            address = address.replace(' ', '  ')  # Çift boşluk
        return address
    
    def _remove_punctuation(self, address: str, clean_data: Dict) -> str:
        """Noktalama işaretlerini kaldır"""
        if random.random() < 0.4:
            address = address.replace(',', '').replace('.', '').replace(':', '')
        return address
    
    def _mix_case(self, address: str, clean_data: Dict) -> str:
        """Karışık büyük/küçük harf"""
        if random.random() < 0.2:
            return address.upper()
        elif random.random() < 0.2:  
            return address.lower()
        return address
    
    def _add_noise_words(self, address: str, clean_data: Dict) -> str:
        """Gürültü kelimeler ekle"""
        noise_words = ['yakını', 'karşısı', 'yanında', 'arka', 'ön']
        
        if random.random() < 0.15:
            noise = random.choice(noise_words)
            components = address.split(', ')
            insert_pos = random.randint(0, len(components))
            components.insert(insert_pos, noise)
            address = ', '.join(components)
        
        return address
    
    def generate_dataset(self, total_samples: int = 10000) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Ana veri seti üretim metodu"""
        print(f"🏭 {total_samples:,} örnek sentetik Türkçe adres veri seti üretiliyor...")
        
        # Unique lokasyonlar için target ID map
        location_to_target_id = {}
        dataset = []
        
        # İlk olarak unique lokasyonlar üret
        unique_locations = []
        num_unique_locations = total_samples // 4  # Ortalama 4 varyasyon per lokasyon
        
        print(f"📍 {num_unique_locations:,} unique fiziksel lokasyon üretiliyor...")
        
        for i in range(num_unique_locations):
            clean_data = self.generate_clean_address()
            # Lokasyonu unique hale getiren key
            location_key = f"{clean_data['city']}_{clean_data['district']}_{clean_data['neighborhood']}_{clean_data['street_name']}_{clean_data['building_no']}"
            
            target_id = str(uuid.uuid4())[:8]  # 8 karakter unique ID
            location_to_target_id[location_key] = target_id
            unique_locations.append(clean_data)
        
        print(f"📝 Adres varyasyonları üretiliyor...")
        
        # Her unique lokasyon için 1-6 arası varyasyon üret
        for i, location_data in enumerate(unique_locations):
            if i % 1000 == 0:
                print(f"   İşlenen lokasyon: {i:,}/{len(unique_locations):,}")
            
            location_key = f"{location_data['city']}_{location_data['district']}_{location_data['neighborhood']}_{location_data['street_name']}_{location_data['building_no']}"
            target_id = location_to_target_id[location_key]
            
            # Bu lokasyon için varyasyon sayısı
            num_variations = random.randint(1, 6)
            
            for _ in range(num_variations):
                if len(dataset) >= total_samples:
                    break
                
                # Temiz adres (train için)
                clean_address = location_data['clean_address']
                
                # Bozuk adres (test için)
                corrupted_address = self.corrupt_address(location_data)
                
                # Koordinatlara küçük varyasyon (aynı bina farklı ölçümler)
                lat_var, lon_var = self.generate_coordinate_variation(
                    location_data['latitude'], location_data['longitude'], radius_km=0.1
                )
                
                dataset.append({
                    'address_text': corrupted_address,
                    'clean_address': clean_address, 
                    'latitude': lat_var,
                    'longitude': lon_var,
                    'target_id': target_id,
                    'city': location_data['city'],
                    'district': location_data['district'],
                    'neighborhood': location_data['neighborhood']
                })
            
            if len(dataset) >= total_samples:
                break
        
        # DataFrame'e çevir
        df = pd.DataFrame(dataset[:total_samples])
        
        print(f"✅ {len(df):,} toplam örnek üretildi")
        print(f"🎯 {df['target_id'].nunique():,} unique target ID")
        print(f"📊 Target ID başına ortalama {len(df) / df['target_id'].nunique():.1f} varyasyon")
        
        # Train/Test ayırımı (%80/%20)
        df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        train_size = int(0.8 * len(df_shuffled))
        
        train_df = df_shuffled[:train_size].copy()
        test_df = df_shuffled[train_size:].copy()
        
        # Train seti: temiz adres + target_id
        train_final = train_df[['address_text', 'clean_address', 'target_id', 'latitude', 'longitude']].copy()
        train_final['id'] = range(len(train_final))
        
        # Test seti: sadece bozuk adres + koordinatlar (target_id gizli)
        test_final = test_df[['address_text', 'latitude', 'longitude']].copy() 
        test_final['id'] = range(len(test_final))
        
        # Test için ground truth kaydet (değerlendirme için)
        self.test_ground_truth = test_df[['target_id']].copy()
        self.test_ground_truth['id'] = range(len(self.test_ground_truth))
        
        return train_final, test_final
    
    def save_dataset(self, train_df: pd.DataFrame, test_df: pd.DataFrame, 
                    output_dir: str = "/Users/tarikozcan/Desktop/adres_hackhaton/kaggle_data"):
        """Veri setini kaydet"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Train seti kaydet
        train_path = f"{output_dir}/train.csv"
        train_df.to_csv(train_path, index=False, encoding='utf-8')
        
        # Test seti kaydet
        test_path = f"{output_dir}/test.csv" 
        test_df.to_csv(test_path, index=False, encoding='utf-8')
        
        # Ground truth kaydet (simülatör için)
        gt_path = f"{output_dir}/ground_truth.csv"
        self.test_ground_truth.to_csv(gt_path, index=False, encoding='utf-8')
        
        print(f"💾 Veri setleri kaydedildi:")
        print(f"   📁 {train_path} ({len(train_df):,} örnek)")
        print(f"   📁 {test_path} ({len(test_df):,} örnek)")
        print(f"   📁 {gt_path} (ground truth)")
        
        # Örnek kayıtları göster
        print(f"\n📋 TRAIN SETİ ÖRNEKLERİ:")
        print(train_df.head(3).to_string())
        
        print(f"\n📋 TEST SETİ ÖRNEKLERİ:")
        print(test_df.head(3).to_string())

def main():
    """Ana üretim fonksiyonu"""
    print("🏁 TEKNOFEST KAGGLE ADRESÇÖZÜMLEME YARIŞMASI SİMÜLATÖRÜ")
    print("=" * 70)
    print("Gerçekçi sentetik Türkçe adres veri seti üretimi başlıyor...\n")
    
    # Veri üreticisi oluştur
    generator = TeknoFestAddressDataGenerator()
    
    # 10,000 örneklik veri seti üret
    train_df, test_df = generator.generate_dataset(total_samples=10000)
    
    # Kaydet
    generator.save_dataset(train_df, test_df)
    
    print(f"\n🎯 KAGGLE YARIŞMA VERİ SETİ HAZIR!")
    print("=" * 70)
    print("✅ Gerçekçi Türkçe adres veri seti üretildi")
    print("✅ Train/Test ayrımı yapıldı (%80/%20)")
    print("✅ Duplicate kayıtlar (aynı adresin farklı yazılışları) mevcut")
    print("✅ Yazım hataları, kısaltmalar, eksik bileşenler eklendi")
    print("✅ Target ID sistemi kuruldu (fiziksel lokasyon eşleştirmesi)")
    print("✅ Koordinat varyasyonları eklendi")
    print("🚀 Yarışma simülasyonu başlatılabilir!")

if __name__ == "__main__":
    main()