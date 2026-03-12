# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Your Name** \
SUNet ID: **Your SUNet ID** \
Citations: **FastAPI docs (https://fastapi.tiangolo.com/), Ollama structured outputs docs (https://ollama.com/blog/structured-outputs), Ollama model library (https://ollama.com/library)** \

This assignment took me about **4-6** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```text
Analyze week2 and implement extract_action_items_llm() using Ollama structured outputs.
Keep the existing heuristic extractor, return a list of strings, and add clear error handling
for invalid model responses or Ollama connection failures.
``` 

Generated Code Snippets:
```text
week2/app/services/extract.py:22-127
week2/app/schemas.py:24-47
week2/app/routers/action_items.py:39-48
```

### Exercise 2: Add Unit Tests
Prompt: 
```text
Add pytest unit tests for extract_action_items_llm() in week2/tests/test_extract.py.
Cover normal extraction, keyword-style inputs, empty input, and invalid structured output.
Mock the Ollama client so tests do not depend on a running model.
``` 

Generated Code Snippets:
```text
week2/tests/test_extract.py:36-80
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```text
Refactor the week2 backend for clearer API contracts and app structure.
Use Pydantic request/response models, move database initialization into FastAPI lifespan,
clean up the SQLite helper layer, and improve API error handling.
``` 

Generated/Modified Code Snippets:
```text
week2/app/main.py:14-35
week2/app/db.py:16-128
week2/app/schemas.py:6-50
week2/app/routers/notes.py:12-34
week2/app/routers/action_items.py:22-80
week2/app/services/extract.py:25-127
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```text
Add a new endpoint for LLM-based extraction and another endpoint to list all notes.
Update the existing week2 frontend so it includes an Extract LLM button and a List Notes button
that call the new API endpoints and render the results.
``` 

Generated Code Snippets:
```text
week2/app/routers/notes.py:20-34
week2/app/routers/action_items.py:30-80
week2/frontend/index.html:151-291
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```text
Read the week2 codebase and generate a concise README.md that explains the project,
setup, how to run the server, available API endpoints, and how to run the tests.
``` 

Generated Code Snippets:
```text
week2/README.md:1-81
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 
