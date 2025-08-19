#!/usr/bin/env python3
"""
TEKNOFEST KAGGLE YARIŞMA SİMÜLATÖRÜ
Gerçek Kaggle yarışma deneyimini simüle eden scoring sistemi
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os
import json
from datetime import datetime

def accuracy_score(y_true, y_pred):
    """Simple accuracy calculation without sklearn"""
    return np.mean(y_true == y_pred)

class TeknoFestKaggleSimulator:
    """TEKNOFEST Adres Çözümleme Yarışması Kaggle Simülatörü"""
    
    def __init__(self, data_dir: str = "/Users/tarikozcan/Desktop/adres_hackhaton/kaggle_data"):
        """Simülatörü başlat"""
        self.data_dir = data_dir
        self.load_data()
        self.setup_evaluation_splits()
        print("🏁 TEKNOFEST KAGGLE YARIŞMA SİMÜLATÖRÜ BAŞLATILDI")
        print("=" * 60)
        print(f"📊 Train Seti: {len(self.train_df):,} örnek")
        print(f"📊 Test Seti: {len(self.test_df):,} örnek")
        print(f"🎯 Unique Target ID: {self.ground_truth_df['target_id'].nunique():,}")
        print(f"📈 Public Leaderboard: {len(self.public_indices):,} örnek (%30)")
        print(f"🔒 Private Leaderboard: {len(self.private_indices):,} örnek (%70)")
        
    def load_data(self):
        """Veri setlerini yükle"""
        train_path = f"{self.data_dir}/train.csv"
        test_path = f"{self.data_dir}/test.csv"
        gt_path = f"{self.data_dir}/ground_truth.csv"
        
        if not all(os.path.exists(p) for p in [train_path, test_path, gt_path]):
            raise FileNotFoundError("Veri setleri bulunamadı! Önce veri üretimini çalıştırın.")
        
        self.train_df = pd.read_csv(train_path)
        self.test_df = pd.read_csv(test_path) 
        self.ground_truth_df = pd.read_csv(gt_path)
        
    def setup_evaluation_splits(self):
        """Public/Private leaderboard ayrımı yap"""
        np.random.seed(42)  # Tutarlı ayrım için
        
        test_size = len(self.test_df)
        indices = np.arange(test_size)
        np.random.shuffle(indices)
        
        # %30 public, %70 private
        public_size = int(0.3 * test_size)
        self.public_indices = sorted(indices[:public_size])
        self.private_indices = sorted(indices[public_size:])
        
    def calculate_address_matching_accuracy(self, predictions: pd.DataFrame, 
                                          evaluation_indices: List[int]) -> float:
        """
        Adres eşleştirme doğruluğu hesapla
        Metrik: Target ID tahmini doğru mu?
        """
        if 'id' not in predictions.columns or 'target_id' not in predictions.columns:
            raise ValueError("Predictions DataFrame'de 'id' ve 'target_id' sütunları olmalı")
        
        # Sadece değerlendirme setindeki indeksleri al
        eval_predictions = predictions[predictions['id'].isin(evaluation_indices)]
        eval_ground_truth = self.ground_truth_df[self.ground_truth_df['id'].isin(evaluation_indices)]
        
        if len(eval_predictions) == 0:
            return 0.0
        
        # ID'lere göre sırala
        eval_predictions = eval_predictions.sort_values('id')
        eval_ground_truth = eval_ground_truth.sort_values('id')
        
        # Tahmin edilen ve gerçek target_id'leri karşılaştır
        predicted_targets = eval_predictions['target_id'].values
        true_targets = eval_ground_truth['target_id'].values
        
        # Doğruluk oranı hesapla
        accuracy = accuracy_score(true_targets, predicted_targets)
        
        return accuracy
    
    def evaluate_submission(self, submission_path: str) -> Dict:
        """
        Submission dosyasını değerlendir ve skorları hesapla
        """
        try:
            # Submission yükle
            submission_df = pd.read_csv(submission_path)
            
            # Format kontrolü
            required_columns = ['id', 'target_id']
            if not all(col in submission_df.columns for col in required_columns):
                return {
                    'error': f"Submission dosyasında {required_columns} sütunları olmalı",
                    'public_score': 0.0,
                    'private_score': 0.0
                }
            
            # Test set boyutu kontrolü
            if len(submission_df) != len(self.test_df):
                return {
                    'error': f"Submission {len(submission_df)} satır, beklenen {len(self.test_df)} satır",
                    'public_score': 0.0,
                    'private_score': 0.0
                }
            
            # Public leaderboard skoru
            public_score = self.calculate_address_matching_accuracy(
                submission_df, self.public_indices
            )
            
            # Private leaderboard skoru (gerçek yarışmada gizli)
            private_score = self.calculate_address_matching_accuracy(
                submission_df, self.private_indices
            )
            
            return {
                'public_score': public_score,
                'private_score': private_score,
                'evaluated_samples_public': len(self.public_indices),
                'evaluated_samples_private': len(self.private_indices),
                'evaluation_metric': 'address_matching_accuracy'
            }
            
        except Exception as e:
            return {
                'error': f"Submission değerlendirme hatası: {str(e)}",
                'public_score': 0.0,
                'private_score': 0.0
            }
    
    def show_public_leaderboard(self, submission_path: str):
        """Public leaderboard skorunu göster (Kaggle gibi)"""
        result = self.evaluate_submission(submission_path)
        
        if 'error' in result:
            print("❌ SUBMISSION HATASI")
            print("=" * 50)
            print(f"Hata: {result['error']}")
            return result
        
        public_score = result['public_score']
        
        print("📊 PUBLIC LEADERBOARD SKORU")
        print("=" * 50)
        print(f"🎯 Adres Eşleştirme Doğruluğu: {public_score:.4f}")
        print(f"📈 Yüzde: {public_score * 100:.2f}%")
        print(f"📊 Değerlendirilen örnek sayısı: {result['evaluated_samples_public']:,}")
        print(f"⚡ Metrik: {result['evaluation_metric']}")
        
        # Performans kategorisi
        if public_score >= 0.90:
            print("🏆 MÜKEMMEL PERFORMANS!")
        elif public_score >= 0.80:
            print("🥇 ÇOK İYİ PERFORMANS!")
        elif public_score >= 0.70:
            print("🥈 İYİ PERFORMANS")
        elif public_score >= 0.60:
            print("🥉 ORTA PERFORMANS")
        else:
            print("🔧 GELİŞTİRİLMESİ GEREKN")
        
        print("=" * 50)
        
        return result
    
    def show_final_results(self, submission_path: str):
        """Yarışma sonu: Private leaderboard skorunu da göster"""
        result = self.evaluate_submission(submission_path)
        
        if 'error' in result:
            print("❌ SUBMISSION HATASI")
            print(f"Hata: {result['error']}")
            return result
        
        public_score = result['public_score']
        private_score = result['private_score']
        
        print("🏁 YARIŞMA SON SONUÇLARI")
        print("=" * 60)
        print(f"📊 PUBLIC LEADERBOARD:  {public_score:.4f} ({public_score * 100:.2f}%)")
        print(f"🔒 PRIVATE LEADERBOARD: {private_score:.4f} ({private_score * 100:.2f}%)")
        print(f"📈 Skor Farkı: {abs(private_score - public_score):.4f}")
        
        # Overfitting kontrolü
        if abs(private_score - public_score) > 0.05:
            print("⚠️  OVERFITTING UYARISI: Public-Private skor farkı yüksek")
        else:
            print("✅ TUTARLI PERFORMANS: Public-Private skorlar yakın")
        
        # Final sıralama
        final_score = private_score  # Gerçek Kaggle'da private score belirleyici
        
        if final_score >= 0.90:
            print("🏆 FINAL SONUÇ: MÜKEMMEL - ÜST SIRALARDA!")
        elif final_score >= 0.80:
            print("🥇 FINAL SONUÇ: ÇOK İYİ - İYİ SIRALAMADA!")
        elif final_score >= 0.70:
            print("🥈 FINAL SONUÇ: İYİ - ORTA ÜSTÜ")
        elif final_score >= 0.60:
            print("🥉 FINAL SONUÇ: ORTA - GELİŞTİRİLEBİLİR")
        else:
            print("🔧 FINAL SONUÇ: ZAYIF - ÇOK GELİŞTİRİLMELİ")
        
        print("=" * 60)
        
        return result
    
    def show_dataset_info(self):
        """Veri seti hakkında bilgi göster"""
        print("📋 KAGGLE VERİ SETİ BILGILERI")
        print("=" * 50)
        
        # Train seti bilgileri
        print("🔹 TRAIN SETİ:")
        print(f"   Toplam örnek: {len(self.train_df):,}")
        print(f"   Sütunlar: {list(self.train_df.columns)}")
        print(f"   Unique target_id: {self.train_df['target_id'].nunique():,}")
        
        # Test seti bilgileri  
        print("\n🔹 TEST SETİ:")
        print(f"   Toplam örnek: {len(self.test_df):,}")
        print(f"   Sütunlar: {list(self.test_df.columns)}")
        
        # Örnek kayıtlar
        print("\n📄 TRAIN ÖRNEKLER:")
        sample_train = self.train_df.head(2)
        for idx, row in sample_train.iterrows():
            print(f"   ID {row['id']}: '{row['address_text'][:60]}...'")
            print(f"           Temiz: '{row['clean_address'][:60]}...'") 
            print(f"           Target: {row['target_id']}")
        
        print("\n📄 TEST ÖRNEKLER:")
        sample_test = self.test_df.head(2)
        for idx, row in sample_test.iterrows():
            print(f"   ID {row['id']}: '{row['address_text'][:60]}...'")
            print(f"           Koordinat: ({row['latitude']:.6f}, {row['longitude']:.6f})")
        
        print("=" * 50)
    
    def create_dummy_submission(self, output_path: str = None):
        """Dummy submission örneği oluştur (baseline)"""
        if output_path is None:
            output_path = f"{self.data_dir}/dummy_submission.csv"
        
        # En basit strateji: rastgele target_id ataması
        np.random.seed(42)
        unique_targets = self.train_df['target_id'].unique()
        
        dummy_predictions = []
        for idx, row in self.test_df.iterrows():
            dummy_target = np.random.choice(unique_targets)
            dummy_predictions.append({
                'id': row['id'],
                'target_id': dummy_target
            })
        
        dummy_df = pd.DataFrame(dummy_predictions)
        dummy_df.to_csv(output_path, index=False)
        
        print(f"🎲 Dummy submission oluşturuldu: {output_path}")
        print(f"   Rastgele target_id ataması yapıldı")
        print(f"   Bu bir baseline referansı - gerçek çözümünüz çok daha iyi olmalı!")
        
        return output_path

def main():
    """Simülatör demo"""
    print("🎮 TEKNOFEST KAGGLE SİMÜLATÖR DEMOsu")
    print("=" * 60)
    
    # Simülatörü başlat
    simulator = TeknoFestKaggleSimulator()
    
    # Veri seti bilgilerini göster
    simulator.show_dataset_info()
    
    # Dummy submission oluştur ve test et
    dummy_path = simulator.create_dummy_submission()
    
    print("\n🧪 DUMMY SUBMISSION TEST:")
    result = simulator.show_public_leaderboard(dummy_path)
    
    print("\n" + "🚀 SİMÜLATÖR HAZIR!")
    print("=" * 60) 
    print("Artık gerçek çözümünüzü geliştirebilir ve test edebilirsiniz:")
    print("1. train.csv ile modelinizi eğitin")
    print("2. test.csv üzerinde tahminler yapın")
    print("3. submission.csv oluşturun (id, target_id sütunları)")
    print("4. show_public_leaderboard() ile skorunuzu görün")
    print("5. show_final_results() ile private skorunuzu görün")

if __name__ == "__main__":
    main()