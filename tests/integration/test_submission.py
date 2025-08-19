#!/usr/bin/env python3
"""
TEKNOFEST KAGGLE SUBMISSION TEST
Çözümü simülatörde test et
"""

from teknofest_competition_simulator import TeknoFestKaggleSimulator

def test_submission():
    """Submission'ı test et"""
    print("🏁 TEKNOFEST KAGGLE SUBMISSION TESTİ")
    print("=" * 70)
    
    # Simülatörü başlat
    simulator = TeknoFestKaggleSimulator()
    
    # Submission dosyası
    submission_path = "/Users/tarikozcan/Desktop/adres_hackhaton/kaggle_data/submission_optimized.csv"
    
    print("\n📊 PUBLIC LEADERBOARD DEĞERLENDİRMESİ:")
    print("-" * 50)
    
    # Public leaderboard skorunu göster
    public_result = simulator.show_public_leaderboard(submission_path)
    
    print("\n🔒 PRIVATE LEADERBOARD DEĞERLENDİRMESİ (Final):")
    print("-" * 50)
    
    # Private leaderboard skorunu da göster (yarışma sonu)
    final_result = simulator.show_final_results(submission_path)
    
    return public_result, final_result

if __name__ == "__main__":
    public, final = test_submission()