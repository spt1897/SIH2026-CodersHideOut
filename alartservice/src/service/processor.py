import logging
from fastapi import FastAPI
import redis.asyncio as redis
from src.model.alert_models import ProcessedAlert
import src.service.dispatcher as client


ALERT_COOLDOWN_SECONDS = 14400  # 4 hours

def classify_cell(p: float) -> tuple[str, float, str]:
    """Applies the Team Leader's Priority Math"""
    if p >= 300:
        c_type = "Confirmed Landslide"
        p_actual = p - 300
    elif p >= 200:
        c_type = "AOT Projected"
        p_actual = p - 200
    elif p >= 100:
        c_type = "Predicted Landslide"
        p_actual = p - 100
    else:
        c_type = "1km Radius of Predicted"
        p_actual = p - 0

    if p_actual >= 75: color = "RED"
    elif p_actual >= 50: color = "ORANGE"
    elif p_actual >= 25: color = "YELLOW"
    else: color = "GREEN"

    return c_type, p_actual, color

async def trigger_dispatch_if_needed(alert: ProcessedAlert, redis_client: redis.Redis, app: FastAPI):
    cooldown_key = f"alert_lock:landslide:{alert.cell_id}"
    
    if alert.alert_color not in ["RED"
                                #  ,"ORANGE"
                                 ]:
        return

    is_new_alert = await redis_client.set(cooldown_key, "locked", ex=ALERT_COOLDOWN_SECONDS, nx=True)
    
    if is_new_alert:
        logging.critical(f"DISPATCHING {alert.alert_color.upper()} ALERT: {alert.cell_type} at Grid {alert.cell_id}")
        await client.push_twilio_sms(alert.cell_id, alert.actual_score)
        await client.push_firebase_notification(alert.cell_id, alert.actual_score,"Landslide warning")
        await client.push_email_alert(alert.cell_id, alert.actual_score)
        await client.push_twilio_voice(alert.cell_id, alert.actual_score, app)
    else:
        logging.debug(f"Grid {alert.cell_id} is critical, but under active cooldown lock.")

async def evaluate_batch(msg_batch: list, redis_client: redis.Redis, groupname: str,app: FastAPI):
    msg_ids_to_ack = []
    
    try:
        for stream, messages in msg_batch:
            for message_id, payload in messages:
                try:
                    count_bytes = payload.get(b"no_of_cells") or payload.get(b"count") or b"1"
                    cells_to_process = int(count_bytes)
                    msg_ids_to_ack.append(message_id)

                    popped_cells = await redis_client.zpopmax("cell_action_priority", cells_to_process)
                    
                    for cell_id_bytes, priority in popped_cells:
                        cell_id = cell_id_bytes.decode("utf-8") # type: ignore
                        c_type, p_actual, color = classify_cell(float(priority))
                        
                        alert = ProcessedAlert(
                            cell_id=cell_id,
                            cell_type=c_type,
                            raw_priority=float(priority),
                            actual_score=p_actual,
                            alert_color=color
                        )
                        
                        await redis_client.xadd("dashboard_alerts_stream", {
                            "cell_id": alert.cell_id,
                            "type": alert.cell_type,
                            "priority_score": str(alert.actual_score),
                            "color": alert.alert_color
                        })
                        
                        await trigger_dispatch_if_needed(alert, redis_client,app)

                except Exception as e:
                    logging.error(f"Failed processing trigger payload: {e}")
                    msg_ids_to_ack.append(message_id)

        if msg_ids_to_ack:
            await redis_client.xack("priority_cells_stream", groupname, *msg_ids_to_ack)

    except Exception as e:
        logging.error(f"Batch evaluation failed: {e}")