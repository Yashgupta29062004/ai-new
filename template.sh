#create the main directory structure
mkdir -p app/agent
mkdir -p app/databases
mkdir -p app/profiles
mkdir -p app/scrapers
mkdir -p app/services
mkdir -p docker
mkdir -p docs

#create files in app agent 

touch app/agent/__init__.py
touch app/agent/base.py
touch app/agent/curator_agent.py
touch app/agent/digest_agent.py
touch app/agent/email_agent.py


#craete files in app data base 

touch app/database/README.md
touch app/database/__init__.py
touch app/database/check_connection.py
touch app/database/connection.py
touch app/database/create_tables.py
touch app/database/models.py
touch app/database/repository.py

# Create files in app/profiles

touch app/profiles/__init__.py
touch app/profiles/user_profile.py

# Create files in app/scrapers
touch app/scrapers/__init__.py
touch app/scrapers/anthropic.py
touch app/scrapers/base.py
touch app/scrapers/openai.py
touch app/scrapers/youtube.py

# Create files in app/services
touch app/services/__init__.py
touch app/services/base.py
touch app/services/email.py
touch app/services/process_anthropic.py
touch app/services/process_curator.py
touch app/services/process_digest.py
touch app/services/process_email.py
touch app/services/process_youtube.py

# Create files in app root
touch app/__init__.py
touch app/config.py
touch app/daily_runner.py
touch app/example.env
touch app/runner.py

# Create files in docker
touch docker/docker-compose.yml

# Create files in docs
touch docs/DEPLOYMENT.md
touch docs/RENDER_SETUP.md

# Create root level files
touch .dockerignore
touch .gitignore
touch .python-version
touch Dockerfile
touch README.md
touch ai-news-aggregator.code-workspace
touch main.py
touch pyproject.toml
touch render.yaml
touch uv.lock

echo "Project structure for AI News Aggregator created successfully!"

