import pytest
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="test", help="Указать окружение для тестов")

@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")

# Функция для записи PID
def record_pid():
    import os
    _PIDS_FILE = os.path.join(os.path.dirname(__file__), '_pids.log')
    
    if 'PYTEST_XDIST_WORKER' not in os.environ:
        try:
            if os.path.exists(_PIDS_FILE):
                os.remove(_PIDS_FILE)
        except Exception:
            pass

    try:
        with open(_PIDS_FILE, 'a') as _f:
            _f.write(f"{os.getpid()} {os.environ.get('PYTEST_XDIST_WORKER','master')}\n")
    except Exception:
        pass

# Фикстура для определения имени сервиса из имени файла
@pytest.fixture(autouse=True)
def set_service_name(request):
    import os
    filename = os.path.basename(request.node.fspath)
    if filename.startswith('test_') and filename.endswith('.py'):
        service_name = filename[5:-3]  # Убираем 'test_' и '.py'
        return service_name
    return "unknown_service"