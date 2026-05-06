# from typing import Optional
# from fastapi import FastAPI, Header

# app = FastAPI()


# # http://localhost:8000/
# # Returns a simple greeting message
# @app.get("/")
# async def read_root():
#     return {"message": "Hello World"}


# # http://localhost:8000/greet?name=Subham&age=18
# # Returns a greeting message with the user's name and age
# # We use query parameters for the name and age where age is 0 by default
# @app.get("/greet")
# async def greet(name: Optional[str] = "User", age: int = 0) -> dict:
#     return {"message": f"Hello {name}", "age": age}


# # Using Base Model we are creating a model to accept post request
# # class Book(BaseModel):
# #     title: str
# #     author: str


# # @app.post(
# #     "/create_book",
# # )
# # async def create_book(
# #     book_data: Book,
# # ):
# #     return {
# #         "title": book_data.title,
# #         "author": book_data.author,
# #     }


# # We are knowing how headers are handled
# # What is a header?
# # A header is a key-value pair that is sent with a request or response
# # Headers are used to pass metadata about the request or response
# # Headers are sent in the request or response line
# # Headers are case-insensitive

# # What are Status Codes?
# # Status codes are used to indicate the status of a request or response
# # Status codes are sent in the response line
# # Status codes are three-digit numbers
# # Status codes are grouped into five categories:
# # 1xx: Informational
# # 2xx: Success
# # 3xx: Redirection
# # 4xx: Client Error
# # 5xx: Server Error

# # Common status codes:
# # 200: OK
# # 201: Created
# # 400: Bad Request
# # 401: Unauthorized
# # 404: Not Found
# # 500: Internal Server Error


# @app.get("/get_headers", status_code=500)
# async def get_headers(
#     accept: str = Header(None),
#     content_type: str = Header(None),
#     user_agent: str = Header(None),
#     host: str = Header(None),
# ):
#     request_headers = {}

#     request_headers["Accept"] = accept
#     request_headers["Content-Type"] = content_type
#     request_headers["User-Agent"] = user_agent
#     request_headers["Host"] = host

#     return request_headers
