
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timezone

app = FastAPI()

events = []
next_event_id = 1


class Event(BaseModel):
    service: str
    severity: str
    message: str


severity_priority = {
    "critical": 1,
    "warning": 2,
    "info": 3
}


@app.get("/")
def home():
    return {"message": "Welcome to IncidentIQ"}


# CREATE EVENT
@app.post("/events")
def create_event(event: Event):
    global next_event_id

    new_event = event.model_dump()

    new_event["id"] = next_event_id
    new_event["created_at"] = datetime.now(timezone.utc)

    events.append(new_event)

    next_event_id += 1

    return {
        "message": "Event received successfully",
        "event": new_event
    }


# GET ALL EVENTS WITH FILTERING, PAGINATION AND SORTING
@app.get("/events")
def get_events(
    severity: str = None,
    service: str = None,
    limit: int = Query(default=10, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    sort_by: str = "severity",
    sort_order: str = "asc"
):
    filtered_events = []

    for event in events:
        if severity and event["severity"] != severity:
            continue

        if service and event["service"] != service:
            continue

        filtered_events.append(event)

    if sort_by == "severity":
        filtered_events.sort(
            key=lambda event: severity_priority.get(
                event["severity"], 4
            ),
            reverse=(sort_order == "desc")
        )

    return filtered_events[skip:skip + limit]


# GET EVENT BY ID
@app.get("/events/{event_id}")
def get_event(event_id: int):

    for event in events:
        if event["id"] == event_id:
            return event

    raise HTTPException(
        status_code=404,
        detail="Event not found"
    )


# DELETE EVENT
@app.delete("/events/{event_id}")
def delete_event(event_id: int):

    for event in events:
        if event["id"] == event_id:
            events.remove(event)

            return {
                "message": "Event deleted successfully",
                "event": event
            }

    raise HTTPException(
        status_code=404,
        detail="Event not found"
    )


# UPDATE EVENT
@app.put("/events/{event_id}")
def update_event(event_id: int, updated_event: Event):

    for event in events:
        if event["id"] == event_id:

            event.update(updated_event.model_dump())

            return {
                "message": "Event updated successfully",
                "event": event
            }

    raise HTTPException(
        status_code=404,
        detail="Event not found"
    )
