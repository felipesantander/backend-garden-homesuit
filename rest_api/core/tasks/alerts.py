from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from core.models import Alert, Data, AlertHistory
from core.services.green_api import send_whatsapp_message
import logging

logger = logging.getLogger(__name__)

def format_duration(seconds):
    """Helper to convert seconds into a human-readable string."""
    if seconds < 60:
        return f"{int(seconds)} segundos"
    minutes = seconds / 60
    if minutes < 60:
        return f"{round(minutes, 1)} minutos"
    hours = minutes / 60
    return f"{round(hours, 1)} horas"

def trigger_alert(alert, machine, triggered_criteria, persistence_seconds=None):
    """
    Function to handle triggered alerts.
    Sends WhatsApp notifications to contacts and logs to history.
    """
    logger.info(f"ALERT TRIGGERED: {alert.name} for machine {machine.serial}. Criteria: {triggered_criteria}")
    
    # Create history record
    AlertHistory.objects.create(
        alert=alert,
        machine=machine,
        details={
            "criteria": triggered_criteria,
            "persistence_seconds": persistence_seconds
        },
        contacts_notified=alert.contacts
    )
    
    # Send WhatsApp notifications
    message = f"🚨 *ALERTA: {alert.name}*\n"
    message += f"Máquina: {machine.serial}\n"
    
    if persistence_seconds:
        message += f"⏱️ *Tiempo persistencia: {format_duration(persistence_seconds)}*\n"
    
    message += "Criterios cumplidos:\n"
    for crit in triggered_criteria:
        message += f"- {crit['channel']}: {crit['condition']} {crit['threshold']}\n"
    
    for contact in alert.contacts:
        phone = contact.get('phone')
        if phone:
            send_whatsapp_message(phone, message)
    
    pass

@shared_task
def monitor_alerts_task():
    """
    Periodic task to monitor data for active alerts.
    """
    from core.models import AlertState
    # Djongo has issues with simple BooleanFilters like is_active=True.
    # Fetching all and filtering in memory is safer here.
    all_alerts = Alert.objects.all().prefetch_related('machines', 'criteria')
    active_alerts = [a for a in all_alerts if a.is_active]
    now = timezone.now()
    
    for alert in active_alerts:
        duration_seconds = alert.duration
        data_frequency = alert.data_frequency
        start_time = now - timedelta(seconds=duration_seconds)
        
        for machine in alert.machines.all():
            logger.info(f"[Monitor] Checking alert '{alert.name}' for machine '{machine.serial}'")
            logger.info(f"[Monitor] Timeframe: {start_time} to {now} (Duration: {duration_seconds}s)")
            all_criteria_met = True
            triggered_details = []
            
            # Global oldest reading timestamp to track persistence
            overall_oldest_reading_time = None
            
            # Fetch or create AlertState for this machine
            state, created = AlertState.objects.get_or_create(alert=alert, machine=machine)
            
            for criterion in alert.criteria.all():
                # Fetch relevant data buckets using PyMongo directly to bypass Djongo bugs
                from core.models.data_manager import DataBucketManager
                db = DataBucketManager.get_db()
                collection = db['core_data']
                
                search_base = start_time.replace(minute=0, second=0, microsecond=0)
                
                # Direct PyMongo query
                query = {
                    "machineId_id": machine.machineId,
                    "channelId_id": criterion.channel.idChannel,
                    "frequency": str(data_frequency),
                    "base_date": {"$gte": search_base}
                }
                logger.info(f"[Monitor] Query: {query}")
                cursor = collection.find(query).sort("base_date", -1)
                data_buckets = list(cursor)
                
                logger.info(f"[Monitor] Criterion: {criterion.channel.name} {criterion.condition} {criterion.threshold}. Found {len(data_buckets)} buckets in Mongo since {search_base}")
                
                relevant_readings = []
                criterion_oldest_reading_time = None
                
                for bucket in data_buckets:
                    # Note: When using PyMongo, we get dictionaries, not model instances
                    readings_list = bucket.get('readings', [])
                    logger.info(f"[Monitor] Investigating bucket with {len(readings_list)} readings.")
                    for reading in readings_list:
                        logger.info(f"-> Analizando reading: {reading}")
                        # Bucketed readings: list of {v: float, t: str, f: str}
                        ts_str = reading.get('t') or reading.get('timestamp')
                        if not ts_str:
                            logger.info("[Monitor] Reading missing timestamp, skipping.")
                            continue
                        
                        try:
                            reading_time = timezone.datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                            logger.info(f"   Timestamp parseado: {reading_time} (vs start_time: {start_time})")
                            logger.info(f"[Monitor] Parsed reading_time: {reading_time} | Threshold start_time: {start_time}")
                            if reading_time >= start_time:
                                relevant_readings.append(reading)
                                # Keep track of the oldest reading time for this criterion
                                if criterion_oldest_reading_time is None or reading_time < criterion_oldest_reading_time:
                                    criterion_oldest_reading_time = reading_time
                                logger.info(f"[Monitor] -> Reading accepted: {reading}")
                            else:
                                logger.info(f"[Monitor] -> Reading too old, rejected.")
                        except (ValueError, TypeError) as e:
                            logger.info(f"[Monitor] Error parsing timestamp '{ts_str}': {e}")
                            continue
                
                logger.info(f"[Monitor] Found {len(relevant_readings)} relevant readings in timeframe.")
                
                if not relevant_readings:
                    logger.info(f"[Monitor] NO readings found for {criterion.channel.name}. Criteria NOT met.")
                    all_criteria_met = False
                    break
                
                condition_persists = True
                for rd in relevant_readings:
                    val = rd.get('v') if 'v' in rd else rd.get('value')
                    if val is None: continue
                    
                    cond = criterion.condition
                    thresh = criterion.threshold
                    
                    is_met = False
                    if cond == '>' and (val > thresh): is_met = True
                    elif cond == '<' and (val < thresh): is_met = True
                    elif cond == '=' and (val == thresh): is_met = True
                    
                    if not is_met:
                        logger.info(f"[Monitor] Value {val} does NOT meet {cond} {thresh}. Condition failed.")
                        condition_persists = False
                        break
                
                if not condition_persists:
                    all_criteria_met = False
                    break
                else:
                    logger.info(f"[Monitor] ALL {len(relevant_readings)} readings met {criterion.channel.name} {criterion.condition} {criterion.threshold}")
                    triggered_details.append({
                        "channel": criterion.channel.name,
                        "condition": criterion.condition,
                        "threshold": criterion.threshold
                    })
                    # Use the oldest reading of the criterion that met the alert to define general persistence
                    # The actual persistence of the whole alert is the minimum duration among criteria
                    # which is equivalent to saying all criteria were met starting from the LATEST of the oldest readings.
                    if overall_oldest_reading_time is None or criterion_oldest_reading_time > overall_oldest_reading_time:
                        overall_oldest_reading_time = criterion_oldest_reading_time
            
            # STATE LOGIC
            if all_criteria_met and alert.criteria.exists():
                state.last_condition_met_at = now
                if state.current_status == 'NORMAL':
                    persistence_seconds = (now - overall_oldest_reading_time).total_seconds() if overall_oldest_reading_time else duration_seconds
                    trigger_alert(alert, machine, triggered_details, persistence_seconds)
                    state.current_status = 'TRIGGERED'
                    state.last_triggered_at = now
                state.save()
            else:
                # Criteria not met
                if state.current_status == 'TRIGGERED':
                    # If 15 minutes have passed since the last time criteria were met, reset to NORMAL
                    if state.last_condition_met_at and (now - state.last_condition_met_at) > timedelta(minutes=15):
                        state.current_status = 'NORMAL'
                        state.save()
                        logger.info(f"Alert {alert.name} for machine {machine.serial} reset to NORMAL after 15m")

    return "Alert monitoring complete."
