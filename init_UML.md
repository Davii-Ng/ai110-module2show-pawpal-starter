classDiagram
    class Owner {
        - id: int
        - name: str
        - phone: str
        - email: str
        - availability: list[TimeWindow]
    }
    class Pet {
        - id: int
        - name: str
        - species: str
        - pickup_time: datetime
        - notes: str
    }
    class Task {
        - id: int
        - type: str
        - duration_minutes: int
        - priority: int
        - price: float
        - pet_id: int
        - earliest_time: datetime
        - latest_time: datetime
        - recurring: bool
    }
    class ScheduleEntry {
        - id: int
        - task_id: int
        - scheduled_start: datetime
        - scheduled_end: datetime
        - reason: str
    }
    class Scheduler {
        + generate_schedule(owner, pets, tasks): ScheduleEntry[]
        + explain(schedule): dict
    }
    class TimeWindow {
        - start: time
        - end: time
    }

    Owner "1" -- "0..*" Pet : owns >
    Owner "1" -- "0..*" TimeWindow : availability >
    Pet "1" -- "0..*" Task : has >
    Task "1" -- "0..1" ScheduleEntry : scheduled as >
    ScheduleEntry "0..*" -- "1" Task : corresponds to >
    Scheduler "1" ..> ScheduleEntry : produces >
    Scheduler "1" ..> Task : consumes >