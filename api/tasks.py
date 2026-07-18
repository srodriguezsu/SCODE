import asyncio
import logging
import pandas as pd
from api.websocket_manager import manager
from api.data_client import fetch_project, fetch_employees, fetch_skills_factors, create_team
from api.recommender import recomendar_equipos

logger = logging.getLogger(__name__)

async def run_recommendation_flow(task_id: str, project_id: int, auth_header: str):
    logger.info(f"Starting recommendation flow for task_id: {task_id}, project_id: {project_id}")
    
    # Step 1: Initial status message
    await manager.broadcast_to_task(task_id, {
        "status": "started",
        "message": "Paso 1/5: Obteniendo la configuración del proyecto..."
    })
    
    try:
        # Step 2: Fetch project settings
        project = await fetch_project(project_id, auth_header)
        team_size = project.get("max_team_size")
        top_n = project.get("max_teams")
        
        logger.info(f"Project configuration fetched: team_size={team_size}, top_n={top_n}")
        if not team_size or not top_n:
            raise ValueError(
                f"El proyecto {project_id} debe tener diligenciados 'max_team_size' y 'max_teams'. "
                f"Se obtuvo max_team_size={team_size}, max_teams={top_n}."
            )
            
        await manager.broadcast_to_task(task_id, {
            "status": "fetching_data",
            "message": "Paso 2/5: Obteniendo la lista de empleados..."
        })
        
        # Step 3: Fetch employees
        employees = await fetch_employees(auth_header)
        if not employees:
            raise ValueError("El API de datos retornó una lista vacía de empleados.")
            
        # Collect employees with skills
        valid_employees = []
        for emp in employees:
            skills = emp.get("skills", [])
            if skills and isinstance(skills, list):
                valid_employees.append(emp)
                
        if not valid_employees:
            raise ValueError("Ningún empleado tiene habilidades asignadas.")
            
        # Determine the target skill.id
        # Take the first skill from the first eligible employee's array
        target_skill_id = valid_employees[0]["skills"][0]["id"]
        logger.info(f"Target skill ID detected: {target_skill_id}")
        
        # Keep only employees whose first skill has target_skill_id
        filtered_employees = []
        for emp in valid_employees:
            first_skill = emp["skills"][0]
            if first_skill.get("id") == target_skill_id:
                filtered_employees.append(emp)
                
        logger.info(f"Filtered {len(filtered_employees)} employees out of {len(employees)} based on skill ID {target_skill_id}")
        
        if len(filtered_employees) < team_size:
            raise ValueError(
                f"No hay suficientes empleados (se encontraron {len(filtered_employees)}) con la habilidad {target_skill_id} "
                f"para formar equipos de tamaño {team_size}."
            )
            
        # Step 4: Fetch factors for this skill ID (replaces TIPOS)
        await manager.broadcast_to_task(task_id, {
            "status": "fetching_factors",
            "message": f"Paso 3/5: Obteniendo los factores para la habilidad con ID {target_skill_id}..."
        })
        
        tipos = await fetch_skills_factors(target_skill_id, auth_header)
        logger.info(f"Skill factors fetched: {tipos}")
        
        # Step 5: Prepare DataFrame and run recommendation algorithm
        df_data = pd.DataFrame([
            {
                "ID": emp["id"],
                "Color Test de predominancia": emp["skills"][0]["factor"]
            }
            for emp in filtered_employees
        ])
        
        from math import comb
        total_combinations = comb(len(df_data), team_size)
        
        await manager.broadcast_to_task(task_id, {
            "status": "running_model",
            "message": f"Paso 4/5: Inicializando ejecución del modelo. Se filtraron {len(df_data)} empleados con el ID de habilidad {target_skill_id}. Total de combinaciones a evaluar: {total_combinations:,}."
        })
        
        loop = asyncio.get_running_loop()
        
        def progress_callback(current, total):
            percentage = (current / total) * 100
            msg = f"Ejecución del modelo: Evaluadas {current:,} / {total:,} combinaciones ({percentage:.1f}%)"
            asyncio.run_coroutine_threadsafe(
                manager.broadcast_to_task(task_id, {
                    "status": "running_model",
                    "message": msg
                }),
                loop
            )
            
        # Run recommendation in a thread pool to avoid blocking the event loop
        top_teams = await asyncio.to_thread(
            recomendar_equipos,
            data=df_data,
            team_size=team_size,
            top_n=top_n,
            tipos=tipos,
            on_progress=progress_callback
        )
        
        logger.info(f"Model generated {len(top_teams)} recommendations.")
        
        if top_teams:
            max_cohesion = top_teams[0]["Indice Cohesion Predicho"]
            min_cohesion = top_teams[-1]["Indice Cohesion Predicho"]
            await manager.broadcast_to_task(task_id, {
                "status": "running_model",
                "message": f"Predicciones del modelo finalizadas. Se generaron {len(top_teams)} perfiles de recomendación. Rango de índice de cohesión en los mejores equipos: {max_cohesion:.4f} a {min_cohesion:.4f}."
            })
        else:
            await manager.broadcast_to_task(task_id, {
                "status": "running_model",
                "message": "Predicciones del modelo finalizadas, pero se generaron 0 perfiles de recomendación."
            })
        
        # Step 6: Save the results to the API
        await manager.broadcast_to_task(task_id, {
            "status": "saving_teams",
            "message": f"Paso 5/5: Guardando {len(top_teams)} equipos recomendados en la base de datos..."
        })
        
        saved_teams = []
        for team in top_teams:
            cohesion = team["Indice Cohesion Predicho"]
            employee_ids = team["IDs"]
            
            # Post each team
            saved_team = await create_team(
                project_id=project_id,
                predicted_cohesion_index=cohesion,
                employee_ids=employee_ids,
                auth_header=auth_header
            )
            saved_teams.append(saved_team)
            
        logger.info("All teams posted successfully.")
        
        # Step 7: Broadcast success and team data
        await manager.broadcast_to_task(task_id, {
            "status": "completed",
            "message": "La recomendación de equipos ha finalizado con éxito.",
            "teams": saved_teams
        })
        
        # Schedule history clean-up in 5 minutes to prevent memory leaks
        asyncio.create_task(clean_task_later(task_id))
        
    except Exception as e:
        logger.error(f"Error in recommendation flow: {str(e)}", exc_info=True)
        await manager.broadcast_to_task(task_id, {
            "status": "failed",
            "message": f"La recomendación ha fallado: {str(e)}"
        })
        # Schedule history clean-up in 5 minutes to prevent memory leaks
        asyncio.create_task(clean_task_later(task_id))

async def clean_task_later(task_id: str, delay: int = 300):
    await asyncio.sleep(delay)
    manager.clean_task(task_id)
