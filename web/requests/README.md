# Requests

## Exception

### RequestException

```python
import time

import requests


N_MAX_API_TRIAL = 3
SEC_TO_SLEEP = 1
n_try = 0
while n_try < N_MAX_API_TRIAL:
    try:
        response = requests.post(api_endpoint, headers=headers, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(SEC_TO_SLEEP)
        n_try += 1
    else:
        print(response.text)
        break
```
