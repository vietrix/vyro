import pytest

from vyro import Vyro
from vyro.errors import HandlerSignatureError
from vyro.middleware.idempotency import IdempotencyKeyMiddleware
from vyro.runtime.backpressure import BackpressureController
from vyro.runtime.authorization import AuthorizationCore
from vyro.runtime.api_keys import APIKeyManager
from vyro.runtime.audit import SecurityAuditLogger
from vyro.runtime.cache import MemoryCacheBackend
from vyro.runtime.cache_invalidation import CacheInvalidationHooks
from vyro.runtime.bulkhead import OutboundBulkhead
from vyro.runtime.circuit_breaker import OutboundCircuitBreaker
from vyro.runtime.compression import ResponseCompressor
from vyro.runtime.concurrency import RouteConcurrencyLimiter
from vyro.runtime.cors import CORSProfile
from vyro.runtime.cron import CronScheduler
from vyro.runtime.csrf import CSRFProtector
from vyro.runtime.db_pool import DBConnectionPoolManager
from vyro.runtime.dead_letter import DeadLetterQueue, JobRetryExecutor
from vyro.runtime.etag import ETagManager
from vyro.runtime.event_bus import InternalEventBus
from vyro.runtime.grpc_gateway import GrpcGateway
from vyro.runtime.http_client import AsyncHttpClient
from vyro.runtime.http2 import Http2StreamManager
from vyro.runtime.jwt_auth import JWTAuthGuard
from vyro.runtime.jobs import JobRuntime
from vyro.runtime.multipart_parser import MultipartParser
from vyro.runtime.multipart_upload import MultipartUploadStream
from vyro.runtime.migrations import MigrationRunner
from vyro.runtime.negotiation import ContentNegotiator
from vyro.runtime.oauth2_oidc import OAUTH2_DEFAULT_CONFIG, OAuth2OIDCHelper
from vyro.runtime.rate_limit import MultiKeyRateLimiter, TokenBucketRateLimiter
from vyro.runtime.response_cache import ResponseCacheService
from vyro.runtime.retry import RetryPolicy
from vyro.runtime.secrets import SecretsManager
from vyro.runtime.shutdown import GracefulShutdownPolicy
from vyro.runtime.sql import SQLiteAsyncAdapter
from vyro.runtime.schema_drift import SchemaDriftDetector
from vyro.runtime.sql_policy import QueryExecutionPolicy
from vyro.runtime.static_files import StaticFileService
from vyro.runtime.timeout_budget import TimeoutBudget
from vyro.runtime.transaction import TransactionScope


def test_sync_handler_is_rejected() -> None:
    app = Vyro()

    with pytest.raises(HandlerSignatureError):

        @app.get("/users/:id")
        def sync_handler(ctx):  # type: ignore[no-untyped-def]
            return {"ok": True}


def test_app_symbol_is_removed() -> None:
    with pytest.raises(ImportError):
        from vyro import App  # type: ignore[attr-defined]  # noqa: F401


def test_first_param_must_be_ctx() -> None:
    app = Vyro()

    with pytest.raises(HandlerSignatureError, match="first argument must be named 'ctx'"):

        @app.get("/users/:id")
        async def invalid(first, id: int):  # type: ignore[no-untyped-def]
            return {"id": id}


def test_handler_must_have_ctx_param() -> None:
    app = Vyro()

    with pytest.raises(HandlerSignatureError, match="must accept first argument 'ctx'"):

        @app.get("/users/:id")
        async def invalid():  # type: ignore[no-untyped-def]
            return {"ok": True}


def test_sync_websocket_handler_is_rejected() -> None:
    app = Vyro()

    with pytest.raises(HandlerSignatureError, match="websocket handler must be declared with async def"):

        @app.websocket("/ws/:room")
        def sync_ws(ctx):  # type: ignore[no-untyped-def]
            return ctx


def test_websocket_handler_is_registered() -> None:
    app = Vyro()

    @app.websocket("/ws/:room")
    async def ws_handler(ctx):  # type: ignore[no-untyped-def]
        return ctx

    assert app._websocket.get("/ws/:room") is ws_handler  # noqa: SLF001


def test_vyro_accepts_custom_shutdown_policy() -> None:
    app = Vyro()
    policy = GracefulShutdownPolicy(timeout_seconds=12, drain_inflight=False)
    app.set_shutdown_policy(policy)
    assert app._shutdown_policy.timeout_seconds == 12  # noqa: SLF001
    assert app._shutdown_policy.drain_inflight is False  # noqa: SLF001


def test_vyro_accepts_custom_idempotency_middleware() -> None:
    app = Vyro()
    middleware = IdempotencyKeyMiddleware()
    app.set_idempotency_middleware(middleware)
    assert app._idempotency is middleware  # noqa: SLF001


def test_vyro_accepts_custom_authorization_core() -> None:
    app = Vyro()
    core = AuthorizationCore()
    app.set_authorization_core(core)
    assert app._authz is core  # noqa: SLF001


def test_vyro_accepts_custom_api_key_manager() -> None:
    app = Vyro()
    manager = APIKeyManager()
    app.set_api_key_manager(manager)
    assert app._api_keys is manager  # noqa: SLF001


def test_vyro_accepts_custom_security_audit_logger() -> None:
    app = Vyro()
    logger = SecurityAuditLogger()
    app.set_security_audit_logger(logger)
    assert app._audit is logger  # noqa: SLF001


def test_vyro_accepts_custom_cache_backend() -> None:
    app = Vyro()
    backend = MemoryCacheBackend()
    app.set_cache_backend(backend)
    assert app._cache is backend  # noqa: SLF001


def test_vyro_accepts_custom_cache_invalidation_hooks() -> None:
    app = Vyro()
    hooks = CacheInvalidationHooks()
    app.set_cache_invalidation_hooks(hooks)
    assert app._cache_invalidation is hooks  # noqa: SLF001


def test_vyro_accepts_custom_backpressure_controller() -> None:
    app = Vyro()
    controller = BackpressureController(max_inflight=8)
    app.set_backpressure(controller)
    assert app._backpressure.max_inflight == 8  # noqa: SLF001


def test_vyro_accepts_custom_concurrency_limiter() -> None:
    app = Vyro()
    limiter = RouteConcurrencyLimiter(default_limit=12)
    app.set_concurrency_limiter(limiter)
    assert app._concurrency.default_limit == 12  # noqa: SLF001


def test_vyro_accepts_custom_rate_limiter() -> None:
    app = Vyro()
    limiter = TokenBucketRateLimiter(rate_per_sec=5.0, burst=10)
    app.set_rate_limiter(limiter)
    assert app._rate_limiter.burst == 10  # noqa: SLF001


def test_vyro_accepts_custom_multi_key_rate_limiter() -> None:
    app = Vyro()
    limiter = MultiKeyRateLimiter(rate_per_sec=12.0, burst=24)
    app.set_multi_rate_limiter(limiter)
    assert app._multi_rate_limiter.burst == 24  # noqa: SLF001


def test_vyro_accepts_custom_http_client() -> None:
    app = Vyro()
    client = AsyncHttpClient()
    app.set_http_client(client)
    assert app._http_client is client  # noqa: SLF001


def test_vyro_accepts_custom_etag_manager() -> None:
    app = Vyro()
    manager = ETagManager()
    app.set_etag_manager(manager)
    assert app._etag is manager  # noqa: SLF001


def test_vyro_accepts_custom_jwt_auth_guard() -> None:
    app = Vyro()
    guard = JWTAuthGuard(secret=b"secret")
    app.set_jwt_auth_guard(guard)
    assert app._jwt is guard  # noqa: SLF001


def test_vyro_accepts_custom_job_runtime() -> None:
    app = Vyro()
    jobs = JobRuntime()
    app.set_job_runtime(jobs)
    assert app._jobs is jobs  # noqa: SLF001


def test_vyro_accepts_custom_cron_scheduler() -> None:
    app = Vyro()
    scheduler = CronScheduler()
    app.set_cron_scheduler(scheduler)
    assert app._cron is scheduler  # noqa: SLF001


def test_vyro_accepts_custom_http2_stream_manager() -> None:
    app = Vyro()
    manager = Http2StreamManager()
    app.set_http2_stream_manager(manager)
    assert app._http2_streams is manager  # noqa: SLF001


def test_vyro_accepts_custom_grpc_gateway() -> None:
    app = Vyro()
    gateway = GrpcGateway()
    app.set_grpc_gateway(gateway)
    assert app._grpc_gateway is gateway  # noqa: SLF001


def test_vyro_accepts_custom_multipart_upload_stream() -> None:
    app = Vyro()
    stream = MultipartUploadStream(boundary=b"abc")
    app.set_multipart_upload(stream)
    assert app._multipart_upload is stream  # noqa: SLF001


def test_vyro_accepts_custom_multipart_parser() -> None:
    app = Vyro()
    parser = MultipartParser()
    app.set_multipart_parser(parser)
    assert app._multipart_parser is parser  # noqa: SLF001


def test_vyro_accepts_custom_migration_runner(tmp_path) -> None:  # type: ignore[no-untyped-def]
    app = Vyro()
    runner = MigrationRunner(database=tmp_path / "app.db", migrations_dir=tmp_path / "migrations")
    app.set_migration_runner(runner)
    assert app._migrations is runner  # noqa: SLF001


def test_vyro_accepts_custom_content_negotiator() -> None:
    app = Vyro()
    negotiator = ContentNegotiator()
    app.set_content_negotiator(negotiator)
    assert app._negotiator is negotiator  # noqa: SLF001


def test_vyro_accepts_custom_oauth2_oidc_helper() -> None:
    app = Vyro()
    helper = OAuth2OIDCHelper(config=OAUTH2_DEFAULT_CONFIG)
    app.set_oauth2_oidc_helper(helper)
    assert app._oauth2 is helper  # noqa: SLF001


def test_vyro_accepts_custom_static_file_service(tmp_path) -> None:  # type: ignore[no-untyped-def]
    app = Vyro()
    static_root = tmp_path / "public"
    static_root.mkdir()
    service = StaticFileService(root=static_root)
    app.set_static_files(service)
    assert app._static_files is service  # noqa: SLF001


def test_vyro_accepts_custom_sql_adapter(tmp_path) -> None:  # type: ignore[no-untyped-def]
    app = Vyro()
    adapter = SQLiteAsyncAdapter(database=tmp_path / "app.db")
    app.set_sql_adapter(adapter)
    assert app._sql is adapter  # noqa: SLF001


def test_vyro_accepts_custom_sql_policy() -> None:
    app = Vyro()
    policy = QueryExecutionPolicy(timeout_sec=3.0, slow_query_threshold_ms=50.0)
    app.set_sql_policy(policy)
    assert app._sql_policy.timeout_sec == pytest.approx(3.0)  # noqa: SLF001


def test_vyro_accepts_custom_schema_drift_detector(tmp_path) -> None:  # type: ignore[no-untyped-def]
    app = Vyro()
    detector = SchemaDriftDetector(database=tmp_path / "app.db")
    app.set_schema_drift_detector(detector)
    assert app._schema_drift is detector  # noqa: SLF001


def test_vyro_accepts_custom_response_compressor() -> None:
    app = Vyro()
    compressor = ResponseCompressor(min_size=1024)
    app.set_response_compressor(compressor)
    assert app._compression.min_size == 1024  # noqa: SLF001


def test_vyro_accepts_custom_cors_profile() -> None:
    app = Vyro()
    profile = CORSProfile.preset("permissive")
    app.set_cors_profile(profile)
    assert app._cors.name == "permissive"  # noqa: SLF001


def test_vyro_accepts_custom_csrf_protector() -> None:
    app = Vyro()
    protector = CSRFProtector(secret=b"test-secret")
    app.set_csrf_protector(protector)
    assert app._csrf is protector  # noqa: SLF001


def test_vyro_accepts_custom_db_pool_manager() -> None:
    app = Vyro()
    manager = DBConnectionPoolManager()
    app.set_db_pool_manager(manager)
    assert app._db_pools is manager  # noqa: SLF001


def test_vyro_accepts_custom_dead_letter_queue() -> None:
    app = Vyro()
    queue = DeadLetterQueue()
    app.set_dead_letter_queue(queue)
    assert app._dead_letter_queue is queue  # noqa: SLF001


def test_vyro_accepts_custom_job_retry_executor() -> None:
    app = Vyro()
    executor = JobRetryExecutor(max_retries=1)
    app.set_job_retry_executor(executor)
    assert app._job_retry is executor  # noqa: SLF001


def test_vyro_accepts_custom_event_bus() -> None:
    app = Vyro()
    bus = InternalEventBus()
    app.set_event_bus(bus)
    assert app._event_bus is bus  # noqa: SLF001


def test_vyro_accepts_custom_secrets_manager() -> None:
    app = Vyro()
    manager = SecretsManager()
    app.set_secrets_manager(manager)
    assert app._secrets is manager  # noqa: SLF001


def test_vyro_accepts_custom_response_cache_service() -> None:
    app = Vyro()
    service = ResponseCacheService()
    app.set_response_cache_service(service)
    assert app._response_cache is service  # noqa: SLF001


def test_vyro_accepts_custom_outbound_circuit_breaker() -> None:
    app = Vyro()
    breaker = OutboundCircuitBreaker(failure_threshold=2, recovery_timeout_sec=1.5)
    app.set_outbound_circuit_breaker(breaker)
    assert app._outbound_circuit_breaker.failure_threshold == 2  # noqa: SLF001


def test_vyro_accepts_custom_outbound_bulkhead() -> None:
    app = Vyro()
    bulkhead = OutboundBulkhead(default_limit=4)
    app.set_outbound_bulkhead(bulkhead)
    assert app._outbound_bulkhead.default_limit == 4  # noqa: SLF001


def test_vyro_accepts_custom_retry_policy() -> None:
    app = Vyro()
    policy = RetryPolicy(max_attempts=5, base_delay_sec=0.2)
    app.set_retry_policy(policy)
    assert app._retry_policy.max_attempts == 5  # noqa: SLF001


def test_vyro_accepts_custom_timeout_budget() -> None:
    app = Vyro()
    budget = TimeoutBudget(timeout_sec=2.5)
    app.set_timeout_budget(budget)
    assert app._timeout_budget.timeout_sec == pytest.approx(2.5)  # noqa: SLF001


def test_vyro_accepts_custom_transaction_scope() -> None:
    app = Vyro()
    scope = TransactionScope()
    app.set_transaction_scope(scope)
    assert app._transaction is scope  # noqa: SLF001
