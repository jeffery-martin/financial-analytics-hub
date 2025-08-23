import os, re, asyncio, time, requests
from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter, TurnContext, ActivityHandler
from botbuilder.schema import Activity

# ---- Config from env ----
APP_ID = os.getenv("MICROSOFT_APP_ID", "")
APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD", "")
USE_GENIE = os.getenv("USE_GENIE", "false").lower() == "true"

# Databricks (unused for mock unless you flip USE_GENIE=true)
DATABRICKS_HOST = os.getenv("DB_HOST", "")
DB_TOKEN = os.getenv("DB_TOKEN", "")
GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID", "")
GENIE_POLL_SECONDS = int(os.getenv("GENIE_POLL_SECONDS", "3"))
GENIE_POLL_MAX = int(os.getenv("GENIE_POLL_MAX", "60"))

adapter = BotFrameworkAdapter(BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD))
loop = asyncio.get_event_loop()

def ask_genie(question: str) -> str:
    if not (DATABRICKS_HOST and (DB_TOKEN or os.getenv("AZURE_OBO_TOKEN")) and GENIE_SPACE_ID):
        return "Genie not configured (this is a mock). Set DB_HOST, GENIE_SPACE_ID and token to call real Genie."
    headers = {"Authorization": f"Bearer {os.getenv('AZURE_OBO_TOKEN') or DB_TOKEN}"}
    try:
        r = requests.post(
            f"{DATABRICKS_HOST}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/start-conversation",
            headers=headers, json={"content": question}, timeout=30
        )
        r.raise_for_status()
        j = r.json()
        conv_id, msg_id = j["conversation"]["id"], j["message"]["id"]
        for _ in range(GENIE_POLL_MAX):
            g = requests.get(
                f"{DATABRICKS_HOST}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conv_id}/messages/{msg_id}",
                headers=headers, timeout=30
            )
            g.raise_for_status()
            gj = g.json()
            status = gj.get("status")
            if status == "COMPLETED":
                at = gj.get("attachments") or []
                if at and isinstance(at, list):
                    return at[0].get("text") or at[0].get("content") or "Completed (no text)."
                return gj.get("content") or "Completed."
            if status in ("FAILED","CANCELLED"):
                return f"Genie status: {status}"
            time.sleep(GENIE_POLL_SECONDS)
        return "Timed out waiting for Genie."
    except Exception as e:
        return f"Genie request error: {e}"

def fake_genie(q: str) -> str:
    t = (q or "").lower()
    if "q2" in t or "vs q1" in t or "quarter" in t:
        return ("**FakeMed Devices — Q2 vs Q1 (USD)**\n"
                "• Total Revenue: **$1.20B** (+6.3%)\n"
                "• Devices: **$740M** (+8.1%) | CGM: **$310M** (+4.5%) | IB Cons: **$150M** (+2.2%)\n"
                "• Drivers: Price +1.0%, Volume +4.0%, Mix +1.3%\n_(synthetic demo values)_")
    if "region" in t:
        return ("**Revenue by Region (Q2)**\n"
                "US $820M | Canada $60M | LatAm $45M | EMEA $200M | APAC $75M\n_(synthetic demo values)_")
    if any(k in t for k in ["risk","headwind","concern"]):
        return ("**Top risks**\n1) Sensor supply tightness (-1.2%)\n2) Reimbursement delays (-0.6%)\n3) Mix shift (-0.4%)\n_(synthetic demo values)_")
    return ("I’m a demo of Genie in Teams. Try:\n"
            "• \"Q2 revenue vs Q1\"\n• \"Show revenue by region\"\n• \"Top risks this quarter\"")

class Bot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        q = turn_context.activity.text or ""
        reply = ask_genie(q) if USE_GENIE else fake_genie(q)
        await turn_context.send_activity(reply)

bot = Bot()
app = Flask(__name__)

@app.route("/api/messages", methods=["POST"])
def messages():
    if not request.headers.get("Content-Type","").startswith("application/json"):
        return Response(status=415)
    activity = Activity().deserialize(request.json)
    auth = request.headers.get("Authorization", "")
    async def turn(ctx): await bot.on_turn(ctx)
    task = adapter.process_activity(activity, auth, turn)
    try:
        loop.run_until_complete(task); return Response(status=201)
    except Exception as e:
        print("Error:", e); return Response(status=500)

@app.route("/", methods=["GET"])
def health(): return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 3978)))
