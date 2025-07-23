import logging, os
from from_root import from_root
from datetime import datetime

LOG_FILE = f"{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.log"

log_dir = 'custom_logs'

logs_path = os.path.join(from_root(), log_dir, LOG_FILE)

os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=logs_path,
    format="[ %(asctime)s ] %(name)s - %(levelname)s %(message)s",
    level=logging.DEBUG,
)
