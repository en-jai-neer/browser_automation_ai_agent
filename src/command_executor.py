import re
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o")
client = AsyncOpenAI(api_key=api_key)

async def get_next_command(task_list, commands, page_content, last_error=None):
    """
    Generate the next Playwright command to execute.
    
    Args:
        task_list (list): Current list of subtasks
        commands (str): All commands executed so far
        page_content (str): Current page content
        last_error (str, optional): Error from the last command execution
        
    Returns:
        str: Next command to execute
    """
    playwright_command_prompt = f"""
    You are an assistant tasked with generating executable code snippets for Playwright and Python. Output Playwright commands to perform web operations or Python commands to store web content in a list named `final_result`. 
    Avoid using JavaScript decorators and backticks.
    \n
    Task List:
    {task_list}
    \n
    Executed Command Till Now:
    {commands}
    \n
    Current Page Content:
    {page_content}
    \n
    {"Previous command resulted in error: " + last_error if last_error else "No errors from previous commands."}
    \n
    Based on this context, output the necessary code to complete the next step in the task list. Ensure the code is suitable for sequential execution.
    Just output the code, nothing else. Also output will be just one-line code that needs to be executed next. Add await to the command if necessary.
    If you want to store the result of the command use the final_result variable.
    Examples:
    - await page.click("text=Submit")
    - await page.fill('input[name="search"]', "search term")
    - final_result = await page.evaluate("() => document.querySelector('h1').innerText")
    \n
    """
    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": playwright_command_prompt},
            {"role": "user", "content": f"What should be the next playwright command?"},
        ]
    )
    return completion.choices[0].message.content.strip()


def extract_code(output):
    """
    Extract code from a string that might contain markdown formatting.
    
    Args:
        output (str): String potentially containing code blocks
        
    Returns:
        str: Extracted code
    """
    # Define a regex pattern to match the code block
    pattern = r"```python\n(.*?)\n```"
    # Search for the pattern in the output string
    match = re.search(pattern, output, re.DOTALL)
    # If a match is found, return the captured group
    if match:
        return match.group(1)
    else:
        return output


async def exec_async(code, page, final_result):
    """
    Safely execute async code with proper error handling.
    
    Args:
        code (str): Code to execute
        page: Playwright page object
        final_result: Variable to store results
        
    Returns:
        tuple: (result, final_result, error)
    """
    # Create a local namespace with page and final_result available
    local_vars = {'page': page, 'final_result': final_result}
    
    # Add await if needed for async Playwright operations
    async_operations = ["page.", "browser.", "playwright.", "sleep(", "asyncio.", "gather("]
    needs_await = any(op in code for op in async_operations) and not (
        code.strip().startswith("await ") or 
        code.strip().startswith("return ") or
        code.strip().startswith("if ") or
        code.strip().startswith("for ") or
        code.strip().startswith("while ") or
        "=" in code and not code.strip().endswith("=")
    )

    if needs_await and not code.strip().startswith("await ") and not code.strip().startswith("return "):
        code = f"await {code}"
    
    # Define the async function in the local namespace
    exec(f"async def __temp():\n    {code}", local_vars)
    
    # Get the function and await it
    temp_func = local_vars['__temp']
    try:
        result = await temp_func()
        # Return the result, modified final_result, and no error
        return result, local_vars['final_result'], None
    except Exception as e:
        # Return None as result, unchanged final_result, and the error
        return None, final_result, str(e)