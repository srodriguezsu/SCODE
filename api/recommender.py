import numpy as np
import pandas as pd
import joblib
from collections import Counter
from itertools import combinations
import logging
from api.config import MODEL_PATH

logger = logging.getLogger(__name__)

# Load the model once when the recommender module is imported
try:
    logger.info(f"Loading decision tree model from {MODEL_PATH}...")
    model = joblib.load(MODEL_PATH)
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load pickle model from {MODEL_PATH}: {str(e)}", exc_info=True)
    raise RuntimeError(f"Failed to load pickle model from {MODEL_PATH}: {str(e)}")

def calcular_shannon(proporciones):
    proporciones = [p for p in proporciones if p > 0]
    if len(proporciones) == 0:
        return 0.0
    return -sum(p * np.log(p) for p in proporciones)

def calcular_balance(proporciones):
    proporciones = [p for p in proporciones if p > 0]
    if len(proporciones) <= 1:
        return 0.0
    return 1.0 - np.std(proporciones)

def recomendar_equipos(data: pd.DataFrame, team_size: int = 4, top_n: int = 10, tipos: list = None) -> list:
    """
    Recommend teams based on diversity, dominance, and balance calculations.
    Uses the loaded Decision Tree model to predict cohesion indices in a batch.
    """
    if tipos is None:
        tipos = [
            'Tipo A - Azul',
            'Tipo B - Verde',
            'Tipo C - Rojo',
            'Tipo D - Naranja'
        ]
        
    comb_indices = list(combinations(data.index, team_size))
    logger.info(f"Total combinations to evaluate: {len(comb_indices)}")
    if not comb_indices:
        return []
        
    ids = data["ID"].values
    factors = data["Color Test de predominancia"].values
    
    diversidades = []
    dominancias = []
    balances = []
    team_ids = []
    
    for combo in comb_indices:
        combo_factors = [factors[i] for i in combo]
        combo_ids = [ids[i] for i in combo]
        
        conteos = Counter(combo_factors)
        
        # Calculate proportions for all types (tipos list)
        proporciones = [conteos.get(t, 0) / team_size for t in tipos]
        
        diversidad = calcular_shannon(proporciones)
        balance = calcular_balance(proporciones)
        dominancia = max(proporciones)
        
        diversidades.append(diversidad)
        dominancias.append(dominancia)
        balances.append(balance)
        team_ids.append(combo_ids)
        
    # Build dataframe for batch prediction
    X = pd.DataFrame({
        "diversidad_shannon": diversidades,
        "dominancia_equipo": dominancias,
        "balance_equipo": balances
    })
    
    # Batch predict using the decision tree model
    cohesions = model.predict(X)
    
    # Store predictions and IDs
    resultados = pd.DataFrame({
        "IDs": team_ids,
        "Indice Cohesion Predicho": cohesions
    })
    
    # Sort by predicted cohesion descending
    resultados = resultados.sort_values(
        "Indice Cohesion Predicho",
        ascending=False
    ).reset_index(drop=True)
    
    top_equipos = resultados.head(top_n)
    
    # Convert numpy types to native Python types before returning to avoid JSON serialization errors
    results_list = []
    for row in top_equipos.itertuples(index=False):
        cohesion_val = float(row[1]) if hasattr(row[1], "item") else row[1]
        member_ids = [int(eid) if hasattr(eid, "item") else eid for eid in row[0]]
        results_list.append({
            "IDs": member_ids,
            "Indice Cohesion Predicho": cohesion_val
        })
        
    return results_list
