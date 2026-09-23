from pydantic_settings import BaseSettings, SettingsConfigDict

class ThresholdConfig:
    def __init__(
        self,
        cpu_high: float = 70.0,
        cpu_critical: float = 90.0,
        memory_high: float = 75.0,
        memory_critical: float = 90.0,
        disk_high: float = 80.0,
        disk_critical: float = 95.0,
        latency_high_ms: float = 100.0,
        latency_critical_ms: float = 150.0,
        error_rate_high: float = 0.03,
        error_rate_critical: float = 0.05,
    ):
        self.cpu_high = cpu_high
        self.cpu_critical = cpu_critical
        self.memory_high = memory_high
        self.memory_critical = memory_critical
        self.disk_high = disk_high
        self.disk_critical = disk_critical
        self.latency_high_ms = latency_high_ms
        self.latency_critical_ms = latency_critical_ms
        self.error_rate_high = error_rate_high
        self.error_rate_critical = error_rate_critical

class Settings(BaseSettings):
    APP_NAME: str = "SmartOps AI Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Mock toggles for local simulation / zero-dependency development
    MOCK_KUBERNETES: bool = True
    MOCK_LLM: bool = True
    MOCK_LOGS: bool = True
    MOCK_DATABASE: bool = True

    # Services endpoints
    USER_SERVICE_URL: str = "http://127.0.0.1:8001"
    ORDER_SERVICE_URL: str = "http://127.0.0.1:8002"
    PAYMENT_SERVICE_URL: str = "http://127.0.0.1:8003"
    SMARTOPS_BACKEND_URL: str = "http://127.0.0.1:8000"

    # MCP Server
    MCP_SERVER_HOST: str = "127.0.0.1"
    MCP_SERVER_PORT: int = 8005

    # Observability & Persistence
    PROMETHEUS_URL: str = "http://localhost:9090"
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    MONGODB_URI: str = "mongodb://localhost:27017/smartops"
    KUBERNETES_NAMESPACE: str = "smartops"

    # Security & Auth
    JWT_SECRET: str = "smartops-ai-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # AI Configuration
    LLM_PROVIDER: str = "mock"  # "mock" | "openai" | "anthropic" | "gemini"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"

    # Configurable Thresholds (Layer 1 Detection)
    CPU_THRESHOLD_HIGH: float = 70.0
    CPU_THRESHOLD_CRITICAL: float = 90.0
    MEMORY_THRESHOLD_HIGH: float = 75.0
    MEMORY_THRESHOLD_CRITICAL: float = 90.0
    DISK_THRESHOLD_HIGH: float = 80.0
    DISK_THRESHOLD_CRITICAL: float = 95.0
    LATENCY_THRESHOLD_HIGH_MS: float = 100.0
    LATENCY_THRESHOLD_CRITICAL_MS: float = 150.0
    ERROR_RATE_THRESHOLD_HIGH: float = 0.03
    ERROR_RATE_THRESHOLD_CRITICAL: float = 0.05

    # Statistical Detection Parameters
    STATISTICAL_WINDOW_SIZE: int = 20
    Z_SCORE_THRESHOLD: float = 2.5
    IQR_MULTIPLIER: float = 1.5

    # ML Anomaly Detection Parameters
    ISOLATION_FOREST_CONTAMINATION: float = 0.05

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
