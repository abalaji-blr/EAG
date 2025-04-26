# Search Assistant

## Objective:

Build a Chrome plugin that:

For every web page that you visit (skip confidential ones like Gmail, WhatsApp, etc), builds a nomic embedding (or any other model that you can run) and then builds an FAISS index with URL
Please remember that you only need the index file, so you can do it on Google Colab and then download this index file as well
When you search within your plugin, it opens the website where that content is and highlights it as well!


## What is the Nomic Embedding Model?
The Nomic embedding model (often referred to as **nomic-embed-text-v1**) is a state-of-the-art open-source embedding model developed by Nomic AI.
Its job is to **convert text into dense vector representations (also known as embeddings)** — that capture the semantic meaning of the input.

These embeddings are used for:

* Semantic search
* Retrieval-augmented generation (RAG)
* Clustering and topic modeling
* Visualizing text datasets (with Nomic’s Atlas tool)

To install, follow the command:
```
pip install sentence_transformers
```

## About FAISS - Vector Database

## Code 

## Demo

