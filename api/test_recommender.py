import os
import pandas as pd
from api.recommender import recomendar_equipos

def run_test():
    # Path to the test data
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "Data", "Datos_Test_Semestres_analisis.csv")
    
    if not os.path.exists(csv_path):
        print(f"Test CSV not found at {csv_path}")
        return
        
    print(f"Loading data from {csv_path}...")
    dataset_raw = pd.read_csv(csv_path)
    data = dataset_raw[['ID', 'Color Test de predominancia']].iloc[:20]
    
    print("Running recommender for team_size=4, top_n=10...")
    recommendations = recomendar_equipos(data, team_size=4, top_n=10)
    
    print("\n--- Top 10 Recommendations ---")
    for idx, rec in enumerate(recommendations):
        print(f"{idx + 1}: Team IDs: {rec['IDs']}, Cohesion Index: {rec['Indice Cohesion Predicho']}")
        
    # Check if the top recommendation matches the notebook's expected value:
    # {'IDs': ['S01001', 'S01002', 'S01004', 'S01008'], 'Indice Cohesion Predicho': 0.8729805801648807}
    expected_ids = ['S01001', 'S01002', 'S01004', 'S01008']
    top_rec = recommendations[0]
    
    # Sort IDs lists to compare them set-wise
    top_ids_sorted = sorted(top_rec["IDs"])
    expected_ids_sorted = sorted(expected_ids)
    
    print("\n--- Verification ---")
    print(f"Top team sorted: {top_ids_sorted}")
    print(f"Expected team sorted: {expected_ids_sorted}")
    print(f"Top team cohesion: {top_rec['Indice Cohesion Predicho']}")
    print("Cohesion matches expected (approx):", abs(top_rec["Indice Cohesion Predicho"] - 0.87298058) < 1e-6)
    
if __name__ == "__main__":
    run_test()
