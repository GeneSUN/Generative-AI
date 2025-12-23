import os
import numpy as np
from redis.commands.search.query import Query
import redis
from openai import OpenAI

class RedisSearch:
    def __init__(self, redis_client, openai_client, text_processor, max_token=4096, debug_message=False):
        self.redis_client = redis_client
        self.openai_client = openai_client
        self.text_processor = text_processor
        self.max_token = max_token
        self.debug_message = debug_message


    def text_search(self, query_text):
        """Perform a text-based search in Redis."""
        query = Query(query_text).return_fields("title", "url", "description")
        results = self.redis_client.ft("posts").search(query)
        
        return [(doc.title, doc.url) for doc in results.docs]

    def embed_query(self, query):
        """Convert the query into an embedding vector."""
        print("Generating embedding for query...")
        embedding = self.openai_client.embeddings.create(input=query, model="text-embedding-ada-002")
        query_vector = embedding.data[0].embedding
        return np.array(query_vector).astype(np.float32).tobytes()



    def hybrid_search(self, query, top_k=3, search_fields="*"):
        """Perform a hybrid vector search in Redis using an embedded query and return top-k results."""
        try:
            query_vector = self.embed_query(query)
            query_obj = Query(f"{search_fields}=>[KNN {top_k} @embedding $vector AS score]") \
                .return_fields("url", "title", "publish_date", "description", "content", "score") \
                .sort_by("score") \
                .dialect(2)

            results = self.redis_client.ft("posts").search(query_obj, query_params={"vector": query_vector})

            if results.total == 0:
                print("No matching results found.")
                return []
            elif results.total < top_k:
                print(f"Only {results.total} results found.")

            return results
        except Exception as e:
            print(f"❌ Redis search error: {e}")
            return []


    def retrieve_relevant_posts(self, query):
        """Retrieve relevant blog posts within a token budget."""
        search_results = self.hybrid_search(query)
        token_budget = self.max_token - self.text_processor.count_tokens(query) - 2000

        if self.debug_message:
            print(f"Token budget: {token_budget}")

        message = ('Use the blog post below to answer the subsequent question. ' \
                   'If the answer cannot be found in the articles, write ' \
                   '"Sorry, I could not find an answer in the blog posts."')
        
        question = f"\n\nQuestion: {query}"

        if search_results:
            for i, post in enumerate(search_results.docs):
                next_post = f'\n\nBlog post:\n"""\n{post.content}\n"""'
                new_token_usage = self.text_processor.count_tokens(message + question + next_post)
                if new_token_usage < token_budget:
                    if self.debug_message:
                        print(f"Token usage: {new_token_usage}")
                    message += next_post
                else:
                    break
        else:
            print("No results found")

        return message + question

    def ask_gpt(self, query : str) -> str:
        message = self.retrieve_relevant_posts( query)
        
        if self.debug_message:
            print(message)
        
        # Ask GPT
        messages = [ 
            {"role": "system", 
            "content": "You answer questions in summary from the blog posts."},
            {"role": "user",
                "content": message},]
        
        if self.debug_message:
            print("Length of messages: ", len(messages))
            if self.debug_message:
                print("Total tokens: ", self.text_processor.count_tokens(messages))
                print(messages)

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.5,
            max_tokens=2000,
            top_p=0.95)
        
        response_message = response.choices[0].message.content
        
        return response_message
    
searcher = RedisSearch(conn, openai_client, text_processor)
searcher.ask_gpt("generative AI advancements")
