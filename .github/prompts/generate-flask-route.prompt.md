---
description: "Generate Flask routes for the LuminaProject based on user specifications"
name: "Generate Flask Route"
argument-hint: "Describe the route to generate, e.g., 'GET /users to fetch all users from database'"
---

Generate a Flask route based on the provided description. Follow the existing patterns in engine.py:

- Use @app.route decorator with appropriate methods
- Connect to the SQLite database using get_db_connection()
- Execute SQL queries and fetch results
- Return JSON responses using jsonify()
- Handle cases where no data is found
- Include proper error handling if needed

Provide the complete route function code that can be added to engine.py.

Description: {user input}

Ensure the route integrates seamlessly with the existing Flask app structure.