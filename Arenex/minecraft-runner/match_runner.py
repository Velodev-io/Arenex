import argparse
import asyncio
import logging
import signal
import time
import json
from redis import asyncio as aioredis
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

from config import (
    POLL_INTERVAL, 
    MATCH_TIME_LIMIT, 
    BOT_API_BASE_PORT,
    BOT_TEMPLATE_PATH,
    REDIS_URL,
    calculate_viewer_port,
)
from bot_process import BotProcess
from inventory_monitor import InventoryMonitor
from result_reporter import mark_live_viewer, report_result

# Setup logging
logging.basicConfig(level=logging.INFO, filename='match_runner.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
console = Console()

def build_match_start_event(match_id, viewer_url, bot1_name, bot2_name):
    return {
        "type": "match_start",
        "match_id": match_id,
        "viewer_url": viewer_url,
        "bot1_name": bot1_name,
        "bot2_name": bot2_name,
    }

def build_state_update_event(match_id, viewer_url, elapsed, sample):
    return {
        "type": "state_update",
        "match_id": match_id,
        "viewer_url": viewer_url,
        "timestamp": time.time(),
        "time_elapsed": elapsed,
        "time_remaining": MATCH_TIME_LIMIT - elapsed,
        "bot1": sample["bot1"],
        "bot2": sample["bot2"],
        "status": "in_progress",
    }

def create_status_table(match_id, bot1_name, bot2_name, poll_data, elapsed_time):
    table = Table(title=f"ARENEX — MINECRAFT WOOD RACE\nMatch: {match_id}")
    table.add_column("Statistic", style="cyan")
    table.add_column(bot1_name, justify="center")
    table.add_column(bot2_name, justify="center")

    def get_val(bot_key, field, default="-"):
        status = poll_data.get(bot_key)
        if not status:
            return "[red]OFFLINE[/red]"
        return str(status.get(field, default))

    # Time info
    time_left = max(0, MATCH_TIME_LIMIT - int(elapsed_time))
    
    # Wood
    wood1 = get_val("bot1", "wood_count", 0)
    wood2 = get_val("bot2", "wood_count", 0)
    table.add_row("Wood Collected", f"{wood1} / 64", f"{wood2} / 64")

    # Position
    pos1 = poll_data.get("bot1", {}).get("position", {})
    pos2 = poll_data.get("bot2", {}).get("position", {})
    p1_str = f"({pos1.get('x',0)}, {pos1.get('y',0)}, {pos1.get('z',0)})" if pos1 else "-"
    p2_str = f"({pos2.get('x',0)}, {pos2.get('y',0)}, {pos2.get('z',0)})" if pos2 else "-"
    table.add_row("Position", p1_str, p2_str)

    # Action
    table.add_row("Action", get_val("bot1", "current_action"), get_val("bot2", "current_action"))

    # Health
    h1 = poll_data.get("bot1", {}).get("health", 0)
    h2 = poll_data.get("bot2", {}).get("health", 0)
    table.add_row("Health", f"❤️  {h1}", f"❤️  {h2}")

    # Footer
    summary = f"Elapsed: {int(elapsed_time)//60}m {int(elapsed_time)%60}s | Time Left: {time_left//60}m {time_left%60}s"
    return Panel(table, subtitle=summary)

async def main():
    parser = argparse.ArgumentParser(description="Arenex Minecraft Match Runner")
    parser.add_argument("--match-id", required=True)
    parser.add_argument("--bot1-script", default=BOT_TEMPLATE_PATH)
    parser.add_argument("--bot2-script", default=BOT_TEMPLATE_PATH)
    parser.add_argument("--bot1-name", default="ArenexBot1")
    parser.add_argument("--bot2-name", default="ArenexBot2")
    parser.add_argument("--bot1-agent-id", required=True)
    parser.add_argument("--bot2-agent-id", required=True)
    args = parser.parse_args()

    console.print(Panel(f"Starting Match: [bold green]{args.match_id}[/bold green]\nBot1: {args.bot1_name}\nBot2: {args.bot2_name}", title="ARENEX"))

    viewer_port = calculate_viewer_port(args.match_id)
    viewer_url = f"http://localhost:{viewer_port}"
    bot1 = BotProcess(args.bot1_name, BOT_API_BASE_PORT, args.match_id, args.bot1_script, viewer_port=viewer_port)
    bot2 = BotProcess(args.bot2_name, BOT_API_BASE_PORT + 1, args.match_id, args.bot2_script, viewer_port=0)

    success1 = await bot1.start()
    success2 = await bot2.start()

    if not success1 or not success2:
        console.print("[bold red]One or both bots failed to start. Aborting match.[/bold red]")
        await bot1.stop()
        await bot2.stop()
        await report_result(args.match_id, "draw", args.bot1_name, args.bot2_name, args.bot1_agent_id, args.bot2_agent_id, 0, 0, 0, "bot_failed_to_start")
        return

    monitor = InventoryMonitor(bot1, bot2)
    start_time = time.time()
    winner = None
    reason = "wood_collected"
    final_poll = {}
    timeline = []

    # Initialize Redis
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    channel = f"match:{args.match_id}:state"

    try:
        await mark_live_viewer(args.match_id)
        await redis.publish(
            channel,
            json.dumps(build_match_start_event(args.match_id, viewer_url, args.bot1_name, args.bot2_name)),
        )

        with Live(console=console, refresh_per_second=1) as live:
            while True:
                elapsed = time.time() - start_time
                if elapsed >= MATCH_TIME_LIMIT:
                    winner = "draw"
                    reason = "time_limit"
                    break

                poll_result = await monitor.poll_once()
                final_poll = poll_result
                live.update(create_status_table(args.match_id, args.bot1_name, args.bot2_name, poll_result, elapsed))

                # Update Timeline
                sample = {
                    "timestamp": elapsed,
                    "bot1": {
                        "position": poll_result.get("bot1", {}).get("position"),
                        "wood_count": poll_result.get("bot1", {}).get("wood_count", 0),
                        "current_action": poll_result.get("bot1", {}).get("current_action"),
                        "health": poll_result.get("bot1", {}).get("health", 0)
                    },
                    "bot2": {
                        "position": poll_result.get("bot2", {}).get("position"),
                        "wood_count": poll_result.get("bot2", {}).get("wood_count", 0),
                        "current_action": poll_result.get("bot2", {}).get("current_action"),
                        "health": poll_result.get("bot2", {}).get("health", 0)
                    }
                }
                timeline.append(sample)

                # Broadcast State
                await redis.publish(
                    channel,
                    json.dumps(build_state_update_event(args.match_id, viewer_url, elapsed, sample)),
                )

                winner_code = await monitor.check_win_condition(poll_result)
                if winner_code:
                    winner = winner_code
                    if monitor.consecutive_failures[bot1.bot_name] >= 3 or monitor.consecutive_failures[bot2.bot_name] >= 3:
                        reason = "opponent_forfeit"
                    break

                await asyncio.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        winner = "draw"
        reason = "manual_abort"
    except Exception as e:
        logger.error(f"Error in match loop: {e}")
        winner = "draw"
        reason = "error"
    finally:
        duration = int(time.time() - start_time)
        console.print(f"\n[bold yellow]Match Finished![/bold yellow] Result: {winner} Reason: {reason}")
        
        await bot1.stop()
        await bot2.stop()

        # Extract final wood counts
        fw1 = final_poll.get("bot1", {}).get("wood_count", 0) if final_poll.get("bot1") else 0
        fw2 = final_poll.get("bot2", {}).get("wood_count", 0) if final_poll.get("bot2") else 0

        # Broadcast Final Summary
        await redis.publish(channel, json.dumps({
            "type": "match_end",
            "match_id": args.match_id,
            "winner": winner,
            "reason": reason,
            "final_wood_bot1": fw1,
            "final_wood_bot2": fw2,
            "duration_seconds": duration,
            "status": "finished"
        }))
        await redis.close()

        await report_result(
            args.match_id, winner, 
            args.bot1_name, args.bot2_name, 
            args.bot1_agent_id, args.bot2_agent_id,
            duration, fw1, fw2, reason,
            timeline
        )

        console.print(Panel(f"Winner: [bold green]{winner}[/bold green]\nDuration: {duration}s\nWood: {fw1} vs {fw2}", title="Match Summary"))

if __name__ == "__main__":
    asyncio.run(main())
