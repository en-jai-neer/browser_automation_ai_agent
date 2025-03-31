import re
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = AsyncOpenAI(api_key=api_key)

def extract_url_with_regex(task):
    """
    Extract URL from a task description using regex.
    
    Args:
        task (str): The task description
        
    Returns:
        str or None: Extracted URL or None if not found
    """
    # This pattern matches most common URL formats
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[\w=&]*)?'
    
    # Search for the pattern in the task string
    match = re.search(url_pattern, task)
    
    if match:
        return match.group(0)  # Return the matched URL
    else:
        return None  # No URL found


async def get_url_from_llm(task):
    """
    Extract URL from a task description using LLM.
    
    Args:
        task (str): The task description
        
    Returns:
        str: Extracted URL
    """
    goto_command_prompt = """
    I am giving you the task that needs to be executed by automation software playwright.
    Your task is just to tell given the task, which URL should playwright go to first.
    Just output url and nothing else
    """
    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": goto_command_prompt},
            {"role": "user", "content": f"What is the URL for this task: {task}"},
        ]
    )
    url = completion.choices[0].message.content.strip()
    return url


async def get_url(task):
    """
    Extract URL from a task description using regex first, then LLM as fallback.
    
    Args:
        task (str): The task description
        
    Returns:
        str: Extracted URL
    """
    url = extract_url_with_regex(task)
    
    if url:
        return url
    else:
        # Fallback to LLM approach if regex doesn't find a URL
        return await get_url_from_llm(task)