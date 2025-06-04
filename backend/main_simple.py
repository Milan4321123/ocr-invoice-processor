print("Starting simplified main.py...")
from fastapi import FastAPI

print("Creating app...")
app = FastAPI()

print("App created successfully!")

@app.get("/")
def root():
    return {"message": "Hello World"}

print("Route added!")

if __name__ == "__main__":
    print("Running directly...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
