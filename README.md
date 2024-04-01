# Vector Search Application for Article Content

This DJango application processes a set of articles, vectorizes their content using text embedding models, and makes the content searchable in a vector database. It supports querying both by text and embeddings to fetch the top K relevant results.

## Features

- **Article Processing**: Automatically fetches and processes articles from specified URLs or local files, supporting a wide range of sources including Wikipedia articles.
- **Text Vectorization**: Leverages open-source text embedding models to convert article text into high-dimensional vectors, enabling semantic search capabilities.
- **Chunk Storage**: Splits articles into manageable chunks and stores their embeddings in a graph-based vector database, optimizing for search efficiency.
- **Search Functionality**: Combines text and vector-based queries, allowing users to search for articles by keywords or semantic similarity and retrieve the most relevant results.
- **Bonus Functionality**: Supports combined text and embedding queries to rerank results based on relevance.
- **User Interface**: Features a web interface for easy submission of search queries and viewing results, enhancing user interaction with the system.
- **Background Processing**: Utilizes Django management command and background tasks to process articles asynchronously, ensuring scalability and responsiveness.
- **Real-time updates on article processing with websocket**: Our system leverages WebSocket technology in conjunction with an ASGI server to facilitate live updates on article processing. This includes real-time notifications about processing stages and progress percentages.
- **Docker Integration**: Comes packaged with Docker and Docker Compose configurations, simplifying setup and deployment across environments.
- **Scalable architecture with services like PostgreSQL, MinIO, Redis, and Milvus.**


## Key Components

- **Django Views**: Serve the frontend and handle form submissions for adding, editing, and deleting articles.
- **Milvus**: A highly scalable vector database that stores embeddings of article chunks for efficient similarity search.
- **PostgreSQL**: The primary relational database for storing article metadata and other application data.
- **Celery**: Used for processing tasks asynchronously, such as populating article chunks and generating embeddings in the background.
- **BERT (Bidirectional Encoder Representations from Transformers) model**: specifically designed to understand the nuances and context of language in text data. The BERT model we've integrated is pre-trained on a vast corpus of multilingual text, making it highly effective for natural language understanding tasks. This model produces embeddings of text data, transforming articles into high-dimensional vectors that capture the semantic essence of the text. Specifically, our system supports embeddings with a dimensionality of 768, a standard size for BERT embeddings that offers a balance between detailed text representation and computational efficiency.

## Workflow
- **Adding Articles**: Users submit articles through a form. The AddArticleView processes the submission, stores the article data in PostgreSQL, and triggers a background task to process the article content into chunks and generate embeddings.

- **Editing and Deleting Articles**: Articles can be modified or removed using the EditArticleView and DeleteArticleView, respectively.

- **Article Chunk Processing**: The task_populate_article_chunks task, executed asynchronously, divides articles into manageable chunks, computes their embeddings using a pre-trained BERT model, and stores these embeddings in Milvus for later retrieval.

- **Searching for Similar Articles**: Users can search for articles by text or direct embedding input. The SearchView handles search requests, querying the Milvus database to find and rank similar article chunks based on the input query's embedding.

- **Fetch a random word from the user's articles, convert this word into its corresponding 768-dimensional vector using the BERT model and return this vector to the user**: by transforming words into vectors, users can directly use these embeddings in the search bar to find similar articles based on vector similarity. This feature bridges the gap between traditional keyword search and more advanced semantic search techniques, allowing users to explore and retrieve content in a way that closely aligns with the conceptual similarity, rather than relying solely on exact keyword matches.

This ability to generate and utilize 768-dimensional vectors from random words exemplifies the application's innovative approach to search and content discovery. It leverages the state-of-the-art in language processing technology to enhance user experience, making the search process both more intuitive and more powerful. Through this feature, users can gain insights into how machine learning models understand and process language, and apply these insights to improve the accuracy and relevance of their search results.

## Real-Time Updates
WebSocket technology, integrated into the application, provides users with real-time feedback on the processing status of articles, including success notifications and progress updates.


## Getting Started

- To add a new article, navigate to /add_article/ and fill out the form.
- To edit an existing article, use the edit link next to each article listed on the main page.
- To delete an article, use the delete link next to the article you wish to remove.
- To perform a search, go to the /search/ page and enter your query (text or embeddings), please also see the embeddings example search



Follow these instructions to get the project up and running on your local machine for development, testing, and deployment purposes.

## Using docker compose
Make sure to install docker and docker compose

If you are using VS code as editor, you can install devcontainers extension and then
vscode will propose to open the project with [devcontainers](https://code.visualstudio.com/docs/remote/containers), which will use the docker setup
Then autocomplete and goto will work out of the box.

The application is containerized for easy setup and reproducibility. Run the following command to start the services:
This command builds the Docker images and starts the containers defined in docker-compose.yml. Wait for all services to start up.


To run in detached mode

```bash
docker-compose up -d
```
Open:

```bash
http://localhost:8000/
```

To view logs/output

```bash
docker-compose logs -f
```
To view logs only for specific service, e.g django service

```bash
docker-compose logs -f django
```



## ASGI Server

ASGI (Asynchronous Server Gateway Interface) is a specification for Python asynchronous web servers and applications. It is designed as an extension to WSGI (Web Server Gateway Interface), the traditional synchronous standard for Python web applications, to support asynchronous web frameworks and applications. ASGI allows for greater scalability and performance, particularly for IO-bound and high-concurrency applications, by enabling non-blocking request processing.
Uvicorn: A lightning-fast ASGI server implementation, often used for running ASGI applications. It's lightweight, super-fast, and supports HTTP/2.


## Local startup and development
	python manage.py makemigrations
	python manage.py migrate
    celery -A vidoso worker -l info -P threads
    uvicorn vidoso.asgi:application --host 0.0.0.0 --port 8000 --reload


## Run tests
    python manage.py test

## Using pre-commit tool

Install [pre-commit][https://pre-commit.com] on your machine and run

```bash
pre-commit install
```

## Add articles 

![Add articcle](/images/add_article.png "Add your articles")


## Search articles in vector DB

![Search article](/images/search.png "Search vector db")

## Fetch random embeddings from your articles
- You can use then this embeddings as search query

![Example embeddings](/images/get_example_vector.png "Example embeddings from your articles")
