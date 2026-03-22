from pawpal_systems import Pet, Task


def test_task_mark_complete():
    t = Task(type="Test", duration_minutes=5)
    assert not t.completed
    t.mark_complete()
    assert t.completed


def test_pet_add_task_increases_count():
    p = Pet(name="Buddy")
    initial = len(p.get_tasks())
    t = Task(type="Feeding", duration_minutes=10)
    p.add_task(t)
    assert len(p.get_tasks()) == initial + 1
    assert t.id in p.task_ids
