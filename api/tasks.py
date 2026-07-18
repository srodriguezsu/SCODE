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
        "message": "Step 1/5: Fetching project configuration..."
    })
    
    try:
        # Step 2: Fetch project settings
        project = await fetch_project(project_id, auth_header)
        team_size = project.get("max_team_size")
        top_n = project.get("max_teams")
        
        logger.info(f"Project configuration fetched: team_size={team_size}, top_n={top_n}")
        if not team_size or not top_n:
            raise ValueError(
                f"Project {project_id} must have both 'max_team_size' and 'max_teams' populated. "
                f"Got max_team_size={team_size}, max_teams={top_n}."
            )
            
        await manager.broadcast_to_task(task_id, {
            "status": "fetching_data",
            "message": "Step 2/5: Fetching employees list..."
        })
        
        # Step 3: Fetch employees
        employees = await fetch_employees(auth_header)
        if not employees:
            raise ValueError("The data API returned an empty list of employees.")
            
        # Collect employees with skills
        valid_employees = []
        for emp in employees:
            skills = emp.get("skills", [])
            if skills and isinstance(skills, list):
                valid_employees.append(emp)
                
        if not valid_employees:
            raise ValueError("No employees have any skills assigned.")
            
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
                f"Not enough employees (found {len(filtered_employees)}) with skill ID {target_skill_id} "
                f"to form teams of size {team_size}."
            )
            
        # Step 4: Fetch factors for this skill ID (replaces TIPOS)
        await manager.broadcast_to_task(task_id, {
            "status": "fetching_factors",
            "message": f"Step 3/5: Fetching skill factors for skill ID {target_skill_id}..."
        })
        
        tipos = await fetch_skills_factors(target_skill_id, auth_header)
        logger.info(f"Skill factors fetched: {tipos}")
        
        # Step 5: Prepare DataFrame and run recommendation algorithm
        await manager.broadcast_to_task(task_id, {
            "status": "running_model",
            "message": "Step 4/5: Running machine learning model predictions..."
        })
        
        df_data = pd.DataFrame([
            {
                "ID": emp["id"],
                "Color Test de predominancia": emp["skills"][0]["factor"]
            }
            for emp in filtered_employees
        ])
        
        # Run recommendation in a thread pool to avoid blocking the event loop
        top_teams = await asyncio.to_thread(
            recomendar_equipos,
            data=df_data,
            team_size=team_size,
            top_n=top_n,
            tipos=tipos
        )
        
        logger.info(f"Model generated {len(top_teams)} recommendations.")
        
        # Step 6: Save the results to the API
        await manager.broadcast_to_task(task_id, {
            "status": "saving_teams",
            "message": f"Step 5/5: Storing {len(top_teams)} recommended teams in the database..."
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
            "message": "Team recommendation finished successfully.",
            "teams": saved_teams
        })
        
    except Exception as e:
        logger.error(f"Error in recommendation flow: {str(e)}", exc_info=True)
        await manager.broadcast_to_task(task_id, {
            "status": "failed",
            "message": f"Recommendation failed: {str(e)}"
        })
