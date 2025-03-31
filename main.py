import asyncio
from src.task_processor import get_task_list, update_task_list, check_if_task_list_completed
from src.url_extractor import get_url
from src.command_executor import get_next_command, exec_async, extract_code
from src.utils.dom_for_llm import DOMSimplifierWrapper
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define the task to execute
task = """Go to Bing. Search for crustdata. click on the first link"""

async def run():
    # Initialize the DOM Simplifier
    dom_simplifier = DOMSimplifierWrapper()

    # Initialize Playwright
    async with async_playwright() as playwright:
        # Launch the browser (headless mode configurable via env variable)
        headless = os.getenv("HEADLESS", "False").lower() == "true"
        browser = await playwright.chromium.launch(headless=headless)
        page = await browser.new_page()

        # Initialize variables
        commands = ""
        final_result = []
        last_error = None
        
        # Break the task into subtasks
        task_list = await get_task_list(task)
        print(f"Initial Task List: {task_list}")

        # Extract the starting URL from the task
        url = await get_url(task)
        print(f"Starting URL: {url}")
        
        # Navigate to the URL
        next_command = f"await page.goto('{url}')"
        result, final_result, error = await exec_async(next_command, page, final_result)
        if error:
            last_error = error
            print(f"Error executing command: {error}")
        commands = commands + "\n" + next_command

        # Get the page content
        page_content = await dom_simplifier.get_dom_for_llm(page)

        # Continue executing tasks until completion
        while (await check_if_task_list_completed(task, task_list, commands, page_content, final_result)).lower() == "true":
            # Update the task list based on current state
            task_list = await update_task_list(task, task_list, commands, page_content, final_result)
            print(f"Updated Task list: {task_list}")
            
            # Determine the next command to execute
            next_command = await get_next_command(task_list, commands, page_content, last_error)
            next_command = extract_code(next_command)
            print(f"Next Command: {next_command}")
            
            # Reset last_error before executing the new command
            last_error = None
            
            # Execute the command and capture any errors
            result, final_result, error = await exec_async(next_command, page, final_result)
            if error:
                last_error = error
                print(f"Error executing command: {error}")
            
            # Update page content and command history
            page_content = await dom_simplifier.get_dom_for_llm(page)
            commands = commands + "\n" + next_command
            print("---------------------------------")

        # Print the final result
        print("\nTask Completed!")
        print("Final Result:", final_result)
        # wait for the five seconds
        await asyncio.sleep(5)
        
        # Close the browser
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
    