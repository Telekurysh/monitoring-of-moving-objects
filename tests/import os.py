import os
import platform
import pytest

# При завершении сессии создаём environment.properties внутри alluredir,
# чтобы Allure показывал информацию о среде выполнения.
def pytest_sessionfinish(session, exitstatus):
    alluredir = session.config.getoption('--alluredir')
    if not alluredir:
        return
    try:
        os.makedirs(alluredir, exist_ok=True)
        env_path = os.path.join(alluredir, 'environment.properties')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f'Python={platform.python_version()}\n')
            f.write(f'Platform={platform.system()} {platform.release()}\n')
            f.write(f'Pytest={pytest.__version__}\n')
    except Exception:
        # не мешаем проходу тестов при ошибках записи
        pass
