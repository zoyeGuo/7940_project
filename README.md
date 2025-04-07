# 7940_project
**Multi-Container Chatbot System**

**Overview**

This project is a multi-container Docker-based chatbot system that integrates three main services:

•	**ChatGPT Service**: A Flask-based service that wraps a ChatGPT API and exposes an HTTP /submit endpoint.

•	**Database Service**: A Flask-based service that interacts with Azure Cosmos DB (using the MongoDB API) to insert and query user data.

•	**Telegram Bot**: A Telegram bot (using python-telegram-bot) that handles user messages, performs intent analysis, extracts required information, and communicates with the ChatGPT and Database services via HTTP.

This microservice architecture allows each component to be independently managed and scaled using Docker Compose.

**Project Architecture**

The project is divided into three containers:

1.	**ChatGPT Service Container**

•	**Purpose**: Receives prompts from other services and forwards them to the ChatGPT API via a custom wrapper (HKBU_ChatGPT). The service listens on port 5000.

•	**Key Files**:

•	ChatGPT_HKBU.py: Custom ChatGPT API wrapper.

•	chatgpt_service.py: Flask application that exposes the /submit endpoint.

•	Dockerfile.chatgpt: Dockerfile for building this container.

2.	**Database Service Container**

•	**Purpose**: Handles database operations (insert and query) using Azure Cosmos DB via the MongoDB API. It listens on port 6000.

•	**Key Files**:

•	db_service.py: Flask application providing endpoints (/insert and /query).

•	Dockerfile.dbservice: Dockerfile for building this container.

3.	**Telegram Bot Container**

•	**Purpose**: Runs the Telegram bot which receives user messages, performs intent analysis (e.g., whether the user wants to play CS:GO), collects required data, and communicates with the ChatGPT and Database services via HTTP.

•	**Key Files**:

•	chatbot_os.py: Telegram bot main application.

•	Dockerfile.telegram: Dockerfile for building this container.

**Project Structure**

```python
my_chatbot_project/
├── .env                       # Environment variables file (contains sensitive data; not committed)
├── docker-compose.yml         # Docker Compose configuration file
├── Dockerfile.chatgpt         # Dockerfile for building the ChatGPT service container
├── Dockerfile.dbservice       # Dockerfile for building the Database service container
├── Dockerfile.telegram        # Dockerfile for building the Telegram bot container
├── chatbot_os.py              # Telegram bot main application
├── ChatGPT_HKBU.py            # Custom ChatGPT API wrapper
├── chatgpt_service.py         # Flask app exposing the /submit endpoint for ChatGPT service
└── db_service.py              # Flask app providing database operations (insert/query)
```

**Environment Variables**

The project configuration relies on environment variables. Create a .env file in the project root with the following content (update with your actual values):

```python
# Telegram Bot configuration
TELEGRAM_ACCESS_TOKEN=your_telegram_bot_token

# ChatGPT service configuration
CHATGPT_BASICURL=https://api.openai.com/v1       # or your ChatGPT API base URL
CHATGPT_MODELNAME=gpt-4
CHATGPT_APIVERSION=2024-xx-xx
CHATGPT_ACCESSTOKEN=your_chatgpt_access_token

# Azure Cosmos DB (MongoDB API) configuration
MONGODB_CONNECTIONSTRING=mongodb+srv://username:password@your-cosmos.documents.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false
MONGODB_DATABASE=your_database_name
MONGODB_COLLECTION=your_collection_name
```

**Docker Compose Configuration**

The docker-compose.yml file defines the three services and their inter-dependencies:

```python
version: "3.8"
services:
  chatgpt:
    build:
      context: .
      dockerfile: Dockerfile.chatgpt
    container_name: chatgpt
    ports:
      - "5000:5000"
    environment:
      - CHATGPT_BASICURL=${CHATGPT_BASICURL}
      - CHATGPT_MODELNAME=${CHATGPT_MODELNAME}
      - CHATGPT_APIVERSION=${CHATGPT_APIVERSION}
      - CHATGPT_ACCESSTOKEN=${CHATGPT_ACCESSTOKEN}

  dbservice:
    build:
      context: .
      dockerfile: Dockerfile.dbservice
    container_name: dbservice
    ports:
      - "6000:6000"
    environment:
      - MONGODB_CONNECTIONSTRING=${MONGODB_CONNECTIONSTRING}
      - MONGODB_DATABASE=${MONGODB_DATABASE}
      - MONGODB_COLLECTION=${MONGODB_COLLECTION}

  telegram:
    build:
      context: .
      dockerfile: Dockerfile.telegram
    container_name: telegram
    environment:
      - TELEGRAM_ACCESS_TOKEN=${TELEGRAM_ACCESS_TOKEN}
      - CHATGPT_SERVICE_URL=http://chatgpt:5000/submit
      - DBSERVICE_URL=http://dbservice:6000
    depends_on:
      - chatgpt
      - dbservice
```

**Building and Running the Project**

1.	**Clone the project repository** and navigate to the project directory:

```python
cd my_chatbot_project
```

2.	**Create the .env file** in the project root and populate it with the required configuration.

3.	**Build and start the containers**:

```python
docker-compose up --build -d
```

4.	**Check container status**:

```bash
docker-compose ps
```

5.	**View logs** (for example, to see Telegram container logs):

```bash
docker-compose logs -f telegram
```

**Testing the Services**

•	**ChatGPT Service**:

Test using curl on the host:

```bash
curl -X POST http://localhost:5000/submit -H "Content-Type: application/json" -d '{"prompt": "Hello"}'
```

•	**Database Service**:

Test the insert and query endpoints:

```bash
curl -X POST http://localhost:6000/insert -H "Content-Type: application/json" -d '{"game_id": "123", "rank": "Gold", "contact": "email@example.com"}'
curl -X GET "http://localhost:6000/query?rank=Gold"
```

•	**Telegram Bot**:

Interact with the bot via the Telegram app using your bot token. Check logs for debugging if necessary:

```bash
docker-compose logs -f telegram
```

**Interact with the Bot**

•	**Search for Your Bot in Telegram**:

Open the Telegram app and search for your bot using its username (set during bot creation with BotFather).

•	**Initiate a Conversation**:

Send a message to your bot. The bot is designed to perform an intent analysis on your message. For example:

•	If you type something like "I want to play csgo", the bot will recognize the intent and respond with:

> “I can help you find other csgo players. Please provide your Game ID, Rank, and Contact Information.”
> 

•	**Provide Additional Information**:

Once the bot enters the information collection state, provide the required details:

•	**Game ID**: Your unique identifier in the game.

•	**Rank**: Your current rank in csgo.

•	**Contact Information**: Your preferred way to be contacted (e.g., email, Discord ID, etc.).

If you do not provide all the required fields at once, the bot will prompt you for the missing fields. For instance, if you only provide Game ID and Rank, it will reply:

> “The following fields are missing from your input, please provide them: contact”
> 

•	**Data Storage and Query**:

After the bot receives all required information, it will send the data to the Database Service. The bot then queries for other users with the same rank and returns a list of players, for example:

```bash
Found the following users with the same rank:
Game ID: 123, Rank: Gold, Contact: user@example.com
Game ID: 456, Rank: Gold, Contact: another@example.com
```

**Regular Conversation**:

For any other message that does not trigger the intent to play csgo, the bot simply forwards your input to the ChatGPT Service and replies with the generated response.

**Conclusion**

This project demonstrates a modular chatbot system built using Docker Compose to manage multiple containers:

•	The **ChatGPT service** handles AI prompt processing.

•	The **Database service** interacts with Azure Cosmos DB for data storage and retrieval.

•	The **Telegram bot** orchestrates user interactions and communicates with the other services via HTTP.

This architecture allows for independent scaling and maintenance of each component. Future improvements may include enhanced error handling, logging, and a more robust API interface.