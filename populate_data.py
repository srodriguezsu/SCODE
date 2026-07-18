import os
import sys
import random
import pandas as pd
import requests

# Predefined lists of Spanish names and surnames to generate random, realistic student records
NOMBRES = [
    "Juan", "Maria", "Carlos", "Ana", "Luis", "Jose", "Laura", "Pedro", "Sofia", "Jorge", 
    "Camila", "Andres", "Daniela", "Mateo", "Valentina", "David", "Lucia", "Alejandro", "Paula", "Diego",
    "Gabriela", "Santiago", "Isabella", "Manuel", "Mariana", "Francisco", "Elena", "Javier", "Sara", "Fernando"
]

APELLIDOS = [
    "Gomez", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Diaz", "Martinez", "Perez", "Romero", 
    "Sanchez", "Ruiz", "Torres", "Alvarez", "Ramirez", "Garcia", "Castro", "Ortiz", "Silva", "Morales", "Herrera",
    "Guzman", "Munoz", "Rojas", "Salazar", "Medina", "Delgado", "Cardona", "Ortega", "Vargas", "Rios"
]


def main():
    print("====================================================")
    print("         SCODE Data Population Script               ")
    print("====================================================")
    
    api_base_url = "https://scode-api-126204309825.us-central1.run.app"
    
    # 1. Request configurations from the user
    try:
        jwt = input("Enter your JWT token (Authorization header): ").strip()
        if not jwt:
            print("Error: JWT is required to authorize requests.")
            return
            
        # Ensure Bearer prefix is included
        if not jwt.lower().startswith("bearer "):
            jwt = f"Bearer {jwt}"
            
        skill_input = input("Enter the Skill ID: ").strip()
        if not skill_input:
            print("Error: Skill ID is required.")
            return
        skill_id = int(skill_input)
        
        limit_input = input("Enter row limit to process (Press Enter for ALL): ").strip()
        limit = int(limit_input) if limit_input.isdigit() else None
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return
    except ValueError:
        print("Error: Invalid inputs. Please enter numbers where appropriate.")
        return
        
    # 2. Check and load CSV data
    csv_path = os.path.join("Data", "Datos_Test_Semestres_analisis.csv")
    if not os.path.exists(csv_path):
        print(f"Error: Could not locate the CSV file at: {csv_path}")
        return
        
    print(f"\nReading {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
        
    if limit:
        df = df.iloc[:limit]
        print(f"Limiting population to the first {limit} records.")
    else:
        print(f"Found {len(df)} records to process.")
        
    headers = {
        "Authorization": jwt,
        "Content-Type": "application/json"
    }
    
    success_count = 0
    print("\nProcessing records...")
    
    for index, row in df.iterrows():
        csv_id = row.get("ID")
        factor = row.get("Color Test de predominancia")
        group = row.get("Etiqueta Semestre-Grupo", "default_group")
        
        # Skip empty rows/factors
        if pd.isna(factor) or not csv_id:
            print(f"[-] Row {index}: Skipped (Empty ID or Factor)")
            continue
            
        # Generate random name and surname
        # national_id should be unique, so we use a large prefix plus row index
        national_id = str(20260000 + index)
        name = random.choice(NOMBRES)
        last_name = random.choice(APELLIDOS)
        
        employee_payload = {
            "national_id": national_id,
            "name": name,
            "last_name": last_name
        }
        
        try:
            # Step A: POST /employees/
            emp_res = requests.post(f"{api_base_url}/employees/", json=employee_payload, headers=headers)
            
            if emp_res.status_code not in (200, 201):
                print(f"[-] Row {index} ({csv_id}): Failed to create employee. Status: {emp_res.status_code}. Response: {emp_res.text}")
                continue
                
            employee = emp_res.json()
            employee_id = employee.get("id")
            
            if not employee_id:
                print(f"[-] Row {index} ({csv_id}): Server response missing employee ID. Response: {employee}")
                continue
                
            # Step B: POST /employees/{employee_id}/skills
            skills_payload = [
                {
                    "skill_id": skill_id,
                    "factor": str(factor)
                }
            ]
            
            skill_res = requests.post(f"{api_base_url}/employees/{employee_id}/skills", json=skills_payload, headers=headers)
            
            if skill_res.status_code not in (200, 201):
                print(f"[-] Row {index} ({csv_id}): Created employee (ID: {employee_id}) but failed to attach skill factor. Status: {skill_res.status_code}. Response: {skill_res.text}")
                continue
                
            print(f"[+] Row {index} ({csv_id}): Populated. Employee ID: {employee_id}. Factor: {factor}")
            success_count += 1
            
        except Exception as err:
            print(f"[-] Row {index} ({csv_id}): Network or client exception occurred: {err}")
            
    print("====================================================")
    print(f"Import Finished. Populated {success_count}/{len(df)} successfully.")
    print("====================================================")

if __name__ == "__main__":
    main()
