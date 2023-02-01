# logger = logging.getLogger("n26")
# logger.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# ch.setFormatter(formatter)
# logger.addHandler(ch)

import json
import uuid

from n26.api import Api
from n26.config import Config

config = Config(validate=False)
config.USERNAME.value = "john.doe@example.com"
config.PASSWORD.value = "$upersecret"
config.LOGIN_DATA_STORE_PATH.value = None
config.DEVICE_TOKEN.value = uuid.uuid4()
config.validate()

api = Api()
statuses = api.get_balance()
json_data = json.dumps(statuses)
print(statuses)
