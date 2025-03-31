import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o")
client = AsyncOpenAI(api_key=api_key)

async def get_task_list(task):
    """
    Break down a high-level task into smaller subtasks.
    
    Args:
        task (str): The high-level task description
        
    Returns:
        list: A list of subtasks
    """
    task_list_creation_prompt = """
    You are an AI assistant that, given a high-level task, will break it down into smaller subtasks. 
    Each subtask should be simple enough to be executed sequentially by the automation tool Playwright without using loops. 
    Return the subtasks as a JSON array of strings, with each string being a single subtask.
    Each step should be actionable and straightforward, ensuring the automation progresses sequentially as it communicates continuously with an external processor for updates.

    Example of the format you should return:
    ["Go to page XYZ.", "Check for the presence of element ABC.", "Fill out form DEF if it is present.", "Click submit button GHI."]
    """
    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": task_list_creation_prompt},
            {"role": "user", "content": f"Write the task list for this task: {task}"},
        ],
        response_format={"type": "json_object"}
    )
    
    response_content = completion.choices[0].message.content.strip()
    task_list = json.loads(response_content)
    
    # Extract the task list from various possible JSON structures
    if isinstance(task_list, dict) and "tasks" in task_list:
        tasks = task_list["tasks"]
    elif isinstance(task_list, dict) and "subtasks" in task_list:
        tasks = task_list["subtasks"]
    elif isinstance(task_list, dict) and "taskList" in task_list:
        tasks = task_list["taskList"]
    else:
        tasks = task_list
    return tasks


async def update_task_list(task, task_list, commands, page_content, final_result):
    """
    Update the task list based on the current execution state.
    
    Args:
        task (str): The original high-level task
        task_list (list): The current list of subtasks
        commands (str): All commands executed so far
        page_content (str): Current page content
        final_result (list): Current final result
        
    Returns:
        list: Updated list of subtasks
    """
    task_list_updation_prompt = f"""
    You are an AI assistant that is helping update a task list based on the current state of execution. 
    Given the original high-level task, the existing task list, the commands that have been executed, 
    the current page content, and the final result, update the task list to reflect what still needs to be done 
    or adjust the approach based on the page's current state.

    ### **Input Data**
    - **Original Task:** {task}
    - **Initial Task List:** {task_list}
    - **Executed Commands:** {commands}
    - **Current Page Content:** {page_content} 
    - **Final Result:** {final_result}

    ### **Task List Update Criteria**
    - Remove tasks that have been executed successfully.
    - Add new tasks if needed based on page content and final result.
    - Ensure each subtask can be executed sequentially by Playwright without loops.
    - Adjust tasks dynamically based on observed changes in the page content and final result.
    - **Ensure that the final desired output is added to the `final_result` variable once all tasks are completed.**

    ### **Response Format**
    Provide the revised list of subtasks as a JSON array of strings.

    **Example Output:**
    ["Go to page XYZ.", "Check for the presence of element ABC.", "Fill out form DEF if it is present.", "Click submit button GHI."]
    """

    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": task_list_updation_prompt},
            {"role": "user", "content": "Write an updated task list based on the current page content and final result."},
        ],
        response_format={"type": "json_object"}
    )
    
    # Extract the updated task list from the completion response
    response_content = completion.choices[0].message.content.strip()
    updated_task_list = json.loads(response_content)
    
    # Handle different possible JSON structures
    if isinstance(updated_task_list, dict):
        tasks = updated_task_list.get(list(updated_task_list.keys())[0], [])
    else:
        tasks = updated_task_list
    
    return tasks


async def check_if_task_list_completed(task, task_list, commands, page_content, final_result):
    """
    Check if all tasks have been completed.
    
    Args:
        task (str): The original high-level task
        task_list (list): The current list of subtasks
        commands (str): All commands executed so far
        page_content (str): Current page content
        final_result (list): Current final result
        
    Returns:
        str: "True" if tasks remain, "False" if all completed
    """
    completed_prompt = f"""
    You are an AI assistant evaluating task completion in an automation workflow using Playwright. 
    Your task is to determine whether all required sub-tasks for a given high-level task have been completed.

    ### **Input Data**
    - **Original Task:** {task}
    - **Sub-Tasks List:** {task_list}
    - **Executed Commands:** {commands}
    - **Current Page Content:** {page_content}
    - **Final Result:** {final_result}

    ### **Decision Criteria**
    - If **all** sub-tasks in the list are completed based on the executed commands, current page content, and final result, return `False`.
    - If **any** sub-task remains incomplete, return `True`.

    ### **Response Format**
    - Return only `True` or `False`, nothing else.
    """

    completion = await client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": completed_prompt}]
    )
    
    # Extract the completion response
    completed = completion.choices[0].message.content.strip()
    return completed