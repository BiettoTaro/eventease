from fastapi import FastAPI

app = FastAPI()

@app.get("/events")
def get_events():
    return [{"title": "hackaton"}, {"title": "Workshop"}]
