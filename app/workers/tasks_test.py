from time import sleep

from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_test.add")
def add(x: int, y: int) -> int:
    """
    Task de teste simples que soma dois números.
    Vamos usar só pra garantir que worker + Redis estão funcionando.
    """
    print(f"[TASK add] Recebido: x={x}, y={y}")
    sleep(2)
    result = x + y
    print(f"[TASK add] Resultado: {result}")
    return result

