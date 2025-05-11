import pytest

def pytest_addoption(parser):
    # Добавляем опцию для выбора окружения
    parser.addoption("--env", action="store", default="test", help="Указать окружение для тестов")

@pytest.fixture(scope="session")
def env(request):
    # Фикстура для доступа к значению опции --env
    return request.config.getoption("--env")

# ...другие фикстуры и конфигурация...
