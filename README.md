# Browser Automation AI Agent

An intelligent web automation framework that combines Playwright with OpenAI's language models to autonomously execute web tasks through natural language instructions.

## Features

-   🤖 Natural language task processing using OpenAI models
-   🔄 Dynamic task planning and execution
-   🌐 Automatic URL extraction from task descriptions
-   📝 Intelligent DOM parsing and simplification for LLM consumption
-   🔧 Error handling and task adaptation based on page content

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/browser-automation-ai-agent.git
cd browser-automation-ai-agent
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:

```bash
playwright install
```

5. Set up your environment variables:

```bash
cp .env.example .env
```

Edit the `.env` file to add your OpenAI API key.

## Usage

1. Define your task in `main.py`:

```python
task = """Go to Bing. Search for Crustdata. Click on the first link."""
```

2. Run the application:

```python
python main.py
```

The agent will:

1. Break down the task into executable subtasks
2. Navigate to the appropriate website
3. Execute the required actions (clicking, typing, etc.)
4. Extract and process the requested information
5. Return the final result

## Project Structure

-   `main.py`: Entry point for the application
-   `src/`: Source code directory
    -   `task_processor.py`: Handles breaking down tasks into subtasks and updating task lists
    -   `url_extractor.py`: Extracts URLs from task descriptions
    -   `command_executor.py`: Executes Playwright commands safely
    -   `utils/`: Utility functions and classes
        -   `dom_simplifier.js`: Simplifies DOM structure
        -   `dom_for_llm.py`: Converts the simplified DOM structure for LLM understanding

## Configuration

Modify the `.env` file to customize the application:

```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini  # or another model of your choice
HEADLESS=False  # Set to True for production use
```

## Advanced Usage

### Custom Task Processing

Create task templates in `task_processor.py` for recurring automation tasks:

```python
SEARCH_TEMPLATE = """
1. Go to the search page
2. Enter {query} in the search box
3. Click the search button
4. Extract the top {num_results} results
"""

# Usage
task = SEARCH_TEMPLATE.format(query="robotics startups", num_results=10)
```
