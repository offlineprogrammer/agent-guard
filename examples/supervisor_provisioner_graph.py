from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from pydantic import BaseModel


# Define the state schema
class State(BaseModel):
    """State passed between Supervisor and Provisioner nodes."""
    task: str
    supervisor_notes: str = ""
    provisioner_status: str = ""


def supervisor_node(state: State) -> Command[State]:
    """
    Supervisor node: receives task and routes to provisioner.
    Updates state with supervisor notes.
    """
    task = state.task
    supervisor_notes = f"Supervisor reviewing: {task}"
    
    # For demo, always route to provisioner
    print(f"[Supervisor] Processing: {task}")
    print(f"[Supervisor] Notes: {supervisor_notes}")
    
    # Return updated state and route to provisioner
    updated_state = State(
        task=task,
        supervisor_notes=supervisor_notes,
        provisioner_status=""
    )
    return Command(
        update=updated_state,
        goto="provisioner"
    )


def provisioner_node(state: State) -> Command[State]:
    """
    Provisioner node: executes the onboarding task.
    Updates state with provisioner status.
    """
    task = state.task
    supervisor_notes = state.supervisor_notes
    
    # Simulate provisioning steps
    provisioner_status = (
        f"✓ Workspace provisioned | "
        f"✓ Email created | "
        f"✓ Access granted | "
        f"✓ Equipment ordered"
    )
    
    print(f"[Provisioner] Executing: {task}")
    print(f"[Provisioner] Status: {provisioner_status}")
    
    # Return final state and end
    updated_state = State(
        task=task,
        supervisor_notes=supervisor_notes,
        provisioner_status=provisioner_status
    )
    return Command(
        update=updated_state,
        goto=END
    )


# Build the graph
graph_builder = StateGraph(State)
graph_builder.add_node("supervisor", supervisor_node)
graph_builder.add_node("provisioner", provisioner_node)

# Set entry point
graph_builder.add_edge(START, "supervisor")

# Compile the graph
graph = graph_builder.compile()


# Run the workflow
if __name__ == "__main__":
    initial_state = State(task="Onboard Sarah Chen as Senior Engineer")
    
    print("\n=== LangGraph Supervisor → Provisioner Workflow ===\n")
    
    # Execute the graph
    final_state_dict = graph.invoke(initial_state.model_dump())
    
    print("\n=== Final State ===")
    print(f"Task: {final_state_dict['task']}")
    print(f"Supervisor Notes: {final_state_dict['supervisor_notes']}")
    print(f"Provisioner Status: {final_state_dict['provisioner_status']}")
