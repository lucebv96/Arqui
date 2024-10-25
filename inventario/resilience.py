from tenacity import retry, stop_after_attempt, wait_fixed
import pybreaker

retry_config = retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
cb = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)


