import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.agent.planner import TaskPlanner
from app.agent.state import TaskPlan, SubTask, TaskStatus
from app.agent.orchestrator import AgentOrchestrator


def test_planner_single_step():
    planner = TaskPlanner()

    # Application launch
    plan1 = planner.create_plan("Open Notepad")
    assert plan1.status == TaskStatus.PENDING
    assert len(plan1.subtasks) == 1
    assert plan1.subtasks[0].tool == "launch_application"
    assert plan1.subtasks[0].args["app_name"] == "notepad"
    assert plan1.subtasks[0].verification_rule == "process_running"

    # Telemetry
    plan2 = planner.create_plan("Check CPU and RAM usage")
    assert plan2.status == TaskStatus.PENDING
    assert len(plan2.subtasks) == 1
    assert plan2.subtasks[0].tool == "get_system_telemetry"
    assert plan2.subtasks[0].verification_rule == "telemetry_present"


def test_planner_multi_step_decomposition():
    planner = TaskPlanner()

    # Compound goal with "and"
    plan = planner.create_plan("Open Notepad and check CPU usage")
    assert plan.status == TaskStatus.PENDING
    assert len(plan.subtasks) == 2
    assert plan.subtasks[0].tool == "launch_application"
    assert plan.subtasks[0].args["app_name"] == "notepad"
    assert plan.subtasks[1].tool == "get_system_telemetry"

    # Compound goal with "then"
    plan2 = planner.create_plan("Open Calculator, then launch Chrome")
    assert plan2.status == TaskStatus.PENDING
    assert len(plan2.subtasks) == 2
    assert plan2.subtasks[0].args["app_name"] == "calculator"
    assert plan2.subtasks[1].args["app_name"] == "chrome"


@pytest.mark.asyncio
async def test_orchestrator_execution_cycle():
    orchestrator = AgentOrchestrator()

    # 1. RECEIVE & PLAN
    plan = await orchestrator.receive_and_plan("Check system status")
    assert plan.status == TaskStatus.PENDING
    assert len(plan.subtasks) == 1

    # 2. RUN PLAN (OBSERVE -> EXECUTE -> VERIFY -> REPORT)
    executed = await orchestrator.run_plan(plan)
    assert executed.status == TaskStatus.COMPLETED
    assert executed.subtasks[0].status == TaskStatus.COMPLETED
    assert executed.subtasks[0].verified is True
    assert "cpu_usage" in executed.subtasks[0].result

    # 3. REPORT
    assert executed.final_report is not None
    assert "INAYA Task Execution Report" in executed.final_report
    assert "Check system status" in executed.final_report


@pytest.mark.asyncio
async def test_orchestrator_cancellation():
    orchestrator = AgentOrchestrator()
    plan = await orchestrator.receive_and_plan("Open Notepad and check CPU")
    assert plan.status == TaskStatus.PENDING

    # Cancel task
    cancelled = await orchestrator.cancel_task(plan.task_id, reason="User test cancellation")
    assert cancelled is True
    assert plan.status == TaskStatus.CANCELLED
    assert all(s.status == TaskStatus.CANCELLED for s in plan.subtasks)


@pytest.mark.asyncio
async def test_tasks_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create and run task synchronously
        create_res = await client.post("/api/tasks", json={
            "objective": "Check CPU and RAM usage",
            "session_id": "test_session",
            "run_sync": True,
        })
        assert create_res.status_code == 200
        data = create_res.json()
        assert data["status"] == "completed"
        task_id = data["task"]["task_id"]
        assert len(data["task"]["subtasks"]) == 1
        assert data["task"]["subtasks"][0]["verified"] is True

        # 2. Query task status
        get_res = await client.get(f"/api/tasks/{task_id}")
        assert get_res.status_code == 200
        assert get_res.json()["task"]["task_id"] == task_id

        # 3. List tasks
        list_res = await client.get("/api/tasks")
        assert list_res.status_code == 200
        assert len(list_res.json()["tasks"]) >= 1


@pytest.mark.asyncio
async def test_orchestrator_notepad_multi_step_task():
    orchestrator = AgentOrchestrator()
    plan = await orchestrator.receive_and_plan("Open Notepad and check CPU usage")
    assert plan.status == TaskStatus.PENDING
    assert len(plan.subtasks) == 2
    assert plan.subtasks[0].tool == "launch_application"
    assert plan.subtasks[0].args["app_name"] == "notepad"
    assert plan.subtasks[1].tool == "get_system_telemetry"

    # Execute plan
    executed = await orchestrator.run_plan(plan)
    assert executed.status == TaskStatus.COMPLETED
    assert executed.subtasks[0].verified is True
    assert executed.subtasks[1].verified is True
    assert "Notepad" in executed.final_report
