"""
Gradio Conversational AI Travel Agent Interface (~30% of UI).
Provides interactive follow-ups, trip modification, and memory-backed travel advice.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path so backend imports work seamlessly
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
load_dotenv()

import gradio as gr
from backend.agent import chat_with_agent, plan_trip
from backend.schemas import TripPlanRequest


def respond(message, chat_history, origin_input, dest_input, mode_input, travelers_input, budget_input):
    """
    Handles conversational interactions, maintains context,
    and returns updated chat history along with tool execution telemetry.
    """
    if not message.strip():
        return "", chat_history, "Ready."

    # Build active trip context if inputs are provided
    current_trip = None
    if origin_input and dest_input:
        current_trip = {
            "origin": origin_input,
            "destination": dest_input,
            "travel_mode": mode_input or "car",
            "travelers": travelers_input or 2,
            "total_budget": budget_input or 1500,
            "currency": "USD"
        }

    # Format history for agent
    formatted_history = []
    for turn in chat_history:
        # Gradio chatbot history can be tuples (user, assistant) or dicts
        if isinstance(turn, (list, tuple)) and len(turn) == 2:
            formatted_history.append({"role": "user", "content": str(turn[0])})
            formatted_history.append({"role": "assistant", "content": str(turn[1])})
        elif isinstance(turn, dict):
            formatted_history.append(turn)

    status_text = "🧠 Atlas Agent reasoning & executing tools..."
    
    reply, tool_logs = chat_with_agent(
        message=message,
        current_trip=current_trip,
        history=formatted_history
    )

    # Append to Gradio history
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": reply})

    log_summary = "Tools Executed: " + (", ".join(tool_logs) if tool_logs else "Direct reasoning")
    return "", chat_history, log_summary


def quick_plan(origin, dest, mode, travelers, budget):
    """Generates an initial quick trip summary to seed the chat context."""
    if not origin or not dest:
        return "⚠️ Please specify both Starting Location and Destination.", []
    
    req = TripPlanRequest(
        origin=origin,
        destination=dest,
        departure_date="2025-07-01",
        return_date="2025-07-06",
        trip_duration_days=5,
        travelers=int(travelers),
        budget=float(budget),
        travel_mode=mode,
        interests=["scenic views", "local cuisine", "culture"]
    )
    
    plan = plan_trip(req)
    summary_md = f"""### 🗺️ Generated Route Plan: {plan.trip_title}
- **Overview:** {plan.overview}
- **Estimated Distance & Time:** {plan.route_details.total_estimated_distance} | {plan.route_details.total_estimated_duration}
- **Budget Allocation:** {plan.currency} {plan.total_budget:,.0f} ({plan.budget_breakdown.budget_tier})
- **Recommended Intermediate Stops:** {', '.join([s.name for s in plan.route_details.stops]) if plan.route_details.stops else 'Direct scenic highway'}
- **Top Attractions:** {', '.join([p.name for p in plan.places_to_visit[:3]])}

*You can now ask follow-up questions or request modifications below!*
"""
    initial_history = [
        {"role": "user", "content": f"Plan a trip from {origin} to {dest} via {mode} for {travelers} people with budget ${budget}."},
        {"role": "assistant", "content": summary_md}
    ]
    return f"✅ Plan generated for {origin} ➔ {dest}", initial_history


# Build Gradio UI with White and Pink theme
theme = gr.themes.Soft(
    primary_hue="pink",
    secondary_hue="rose",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Outfit"), "sans-serif"]
).set(
    body_background_fill="#fdf2f8",
    body_background_fill_dark="#fdf2f8",
    block_background_fill="#ffffff",
    block_background_fill_dark="#ffffff",
    button_primary_background_fill="*primary_500",
    button_primary_background_fill_hover="*primary_600",
    button_primary_text_color="#ffffff",
    border_color_primary="rgba(236, 72, 153, 0.3)"
)

with gr.Blocks(title="Atlas AI Travel Agent") as demo:
    gr.Markdown(
        """
        # 🌸 Atlas AI Agent - Conversational Travel Planner
        ### Powered by LangChain, Groq LLaMA-3.3-70b & Tavily Web Search
        Ask follow-up questions, refine your route, adjust activities, or explore alternative transit options.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Trip Context (Optional)")
            origin_box = gr.Textbox(label="Origin", value="San Francisco, CA", placeholder="e.g. San Francisco, CA")
            dest_box = gr.Textbox(label="Destination", value="Los Angeles, CA", placeholder="e.g. Los Angeles, CA")
            mode_box = gr.Dropdown(
                choices=["car", "bike", "bus", "train", "flight"],
                value="car",
                label="Travel Mode"
            )
            travelers_box = gr.Slider(minimum=1, maximum=10, value=2, step=1, label="Travelers")
            budget_box = gr.Number(value=1800, label="Budget (USD)")
            
            gen_btn = gr.Button("⚡ Generate Base Plan for Chat", variant="secondary")
            status_box = gr.Markdown("Status: Ready.")

        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=520)
            
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Ask Atlas: e.g. 'Suggest scenic stops along Big Sur', 'Add vegan restaurants', 'Can we take a train instead?'",
                    show_label=False,
                    scale=4
                )
                send_btn = gr.Button("Send ✈️", variant="primary", scale=1)

            with gr.Row():
                gr.Markdown("**Quick Prompts:**")
            with gr.Row():
                q1 = gr.Button("🌿 Scenic Detours & Rest Stops", size="sm")
                q2 = gr.Button("🥗 Vegetarian & Local Food Gems", size="sm")
                q3 = gr.Button("🌧️ Rainy Day Contingency Plan", size="sm")
                q4 = gr.Button("🚆 Compare Train vs Driving Route", size="sm")

    # Wire event handlers
    send_btn.click(
        respond,
        inputs=[msg_input, chatbot, origin_box, dest_box, mode_box, travelers_box, budget_box],
        outputs=[msg_input, chatbot, status_box]
    )
    msg_input.submit(
        respond,
        inputs=[msg_input, chatbot, origin_box, dest_box, mode_box, travelers_box, budget_box],
        outputs=[msg_input, chatbot, status_box]
    )

    q1.click(lambda: "What are the most scenic detour viewpoints and rest stops along this route?", outputs=msg_input)
    q2.click(lambda: "Can you recommend top-rated authentic local food and vegetarian options for our destination?", outputs=msg_input)
    q3.click(lambda: "What indoor activities and attractions do you recommend in case of bad weather?", outputs=msg_input)
    q4.click(lambda: "How does taking a train compare to driving in terms of travel time, cost, and scenery?", outputs=msg_input)

    gen_btn.click(
        quick_plan,
        inputs=[origin_box, dest_box, mode_box, travelers_box, budget_box],
        outputs=[status_box, chatbot]
    )


if __name__ == "__main__":
    demo.launch(theme=theme, server_name="0.0.0.0", server_port=7860, share=False)
