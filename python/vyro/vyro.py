from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .middleware import Middleware
from .middleware.idempotency import IdempotencyKeyMiddleware
from .middleware.registry import MiddlewareRegistry
from .routing.registry import RouterRegistry
from .runtime.backpressure import BackpressureController
from .runtime.authorization import AuthorizationCore
from .runtime.api_keys import APIKeyManager
from .runtime.audit import SecurityAuditLogger
from .runtime.cache import CacheBackend, MemoryCacheBackend
from .runtime.cache_invalidation import CacheInvalidationHooks
from .runtime.bulkhead import OutboundBulkhead
from .runtime.canary import CanaryRoutingControls
from .runtime.circuit_breaker import OutboundCircuitBreaker
from .runtime.compression import ResponseCompressor
from .runtime.concurrency import RouteConcurrencyLimiter
from .runtime.cors import CORSProfile
from .runtime.cron import CronScheduler
from .runtime.cqrs import CommandBus, QueryBus
from .runtime.csrf import CSRFProtector
from .runtime.db_pool import DBConnectionPoolManager
from .runtime.dead_letter import DeadLetterQueue, JobRetryExecutor
from .runtime.etag import ETagManager
from .runtime.event_bus import InternalEventBus
from .runtime.feature_flags import FeatureFlagEngine
from .runtime.grpc_gateway import GrpcGateway
from .runtime.http_client import AsyncHttpClient
from .runtime.http2 import Http2StreamManager
from .runtime.jwt_auth import JWTAuthGuard
from .runtime.jobs import JobRuntime
from .runtime.multipart_upload import MultipartUploadStream
from .runtime.multipart_parser import MultipartParser
from .runtime.migrations import MigrationRunner
from .runtime.negotiation import ContentNegotiator
from .runtime.oauth2_oidc import OAUTH2_DEFAULT_CONFIG, OAuth2OIDCHelper
from .runtime.outbox import OutboxPatternHelper
from .runtime.rate_limit import MultiKeyRateLimiter, TokenBucketRateLimiter
from .runtime.response_cache import ResponseCacheService
from .runtime.retry import RetryPolicy
from .runtime.saga import SagaOrchestrator
from .runtime.schema_drift import SchemaDriftDetector
from .runtime.secrets import SecretsManager
from .runtime.shutdown import GracefulShutdownPolicy
from .runtime.server import run_native_server
from .runtime.sql import AsyncSQLAdapter, SQLiteAsyncAdapter
from .runtime.sql_policy import QueryExecutionPolicy
from .runtime.static_files import StaticFileService
from .runtime.tenant import TenantIsolationModel
from .runtime.tenant_routing import TenantRoutingConfig
from .runtime.timeout_budget import TimeoutBudget
from .runtime.transaction import TransactionScope
from .runtime.websocket import WebSocketRouteRegistry
from .settings import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_STATIC_ROOT, DEFAULT_WORKERS


class Vyro:
    def __init__(self) -> None:
        self._router = RouterRegistry()
        self._middlewares = MiddlewareRegistry()
        self._idempotency = IdempotencyKeyMiddleware()
        self._authz = AuthorizationCore()
        self._api_keys = APIKeyManager()
        self._audit = SecurityAuditLogger()
        self._cache: CacheBackend = MemoryCacheBackend()
        self._cache_invalidation = CacheInvalidationHooks()
        self._canary = CanaryRoutingControls()
        self._shutdown_policy = GracefulShutdownPolicy()
        self._backpressure = BackpressureController()
        self._concurrency = RouteConcurrencyLimiter()
        self._rate_limiter = TokenBucketRateLimiter(rate_per_sec=1000.0, burst=2000)
        self._multi_rate_limiter = MultiKeyRateLimiter(rate_per_sec=500.0, burst=1000)
        self._http_client = AsyncHttpClient()
        self._etag = ETagManager()
        self._jwt = JWTAuthGuard(secret=b"vyro-dev-secret")
        self._jobs = JobRuntime()
        self._cron = CronScheduler()
        self._command_bus = CommandBus()
        self._query_bus = QueryBus()
        self._http2_streams = Http2StreamManager()
        self._grpc_gateway = GrpcGateway()
        self._multipart_upload = MultipartUploadStream(boundary=b"vyro-default")
        self._multipart_parser = MultipartParser()
        self._migrations = MigrationRunner(database=Path("app.db"), migrations_dir=Path("migrations"))
        self._negotiator = ContentNegotiator()
        self._oauth2 = OAuth2OIDCHelper(config=OAUTH2_DEFAULT_CONFIG)
        self._outbox = OutboxPatternHelper()
        self._static_files = StaticFileService(root=Path(DEFAULT_STATIC_ROOT))
        self._sql: AsyncSQLAdapter = SQLiteAsyncAdapter(database=Path(":memory:"))
        self._sql_policy = QueryExecutionPolicy()
        self._schema_drift = SchemaDriftDetector(database=Path("app.db"))
        self._compression = ResponseCompressor()
        self._cors = CORSProfile.preset("standard")
        self._csrf = CSRFProtector.with_random_secret()
        self._db_pools = DBConnectionPoolManager()
        self._dead_letter_queue = DeadLetterQueue()
        self._job_retry = JobRetryExecutor(dead_letter_queue=self._dead_letter_queue)
        self._event_bus = InternalEventBus()
        self._feature_flags = FeatureFlagEngine()
        self._secrets = SecretsManager()
        self._response_cache = ResponseCacheService(backend=self._cache)
        self._saga = SagaOrchestrator()
        self._outbound_circuit_breaker = OutboundCircuitBreaker()
        self._outbound_bulkhead = OutboundBulkhead()
        self._retry_policy = RetryPolicy()
        self._tenant_isolation = TenantIsolationModel()
        self._tenant_routing = TenantRoutingConfig()
        self._timeout_budget = TimeoutBudget(timeout_sec=30.0)
        self._transaction = TransactionScope()
        self._websocket = WebSocketRouteRegistry()

    def get(
        self,
        path: str,
        *,
        version: str | None = None,
        deprecated: bool | str = False,
        tenant: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        routed_path, resolved_tenant = self._tenant_routing.apply(path, tenant)
        return self._router.add_route(
            "GET",
            routed_path,
            version=version,
            deprecated=deprecated,
            tenant=resolved_tenant,
        )

    def post(
        self,
        path: str,
        *,
        version: str | None = None,
        deprecated: bool | str = False,
        tenant: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        routed_path, resolved_tenant = self._tenant_routing.apply(path, tenant)
        return self._router.add_route(
            "POST",
            routed_path,
            version=version,
            deprecated=deprecated,
            tenant=resolved_tenant,
        )

    def put(
        self,
        path: str,
        *,
        version: str | None = None,
        deprecated: bool | str = False,
        tenant: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        routed_path, resolved_tenant = self._tenant_routing.apply(path, tenant)
        return self._router.add_route(
            "PUT",
            routed_path,
            version=version,
            deprecated=deprecated,
            tenant=resolved_tenant,
        )

    def delete(
        self,
        path: str,
        *,
        version: str | None = None,
        deprecated: bool | str = False,
        tenant: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        routed_path, resolved_tenant = self._tenant_routing.apply(path, tenant)
        return self._router.add_route(
            "DELETE",
            routed_path,
            version=version,
            deprecated=deprecated,
            tenant=resolved_tenant,
        )

    def websocket(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(handler: Callable[..., Any]) -> Callable[..., Any]:
            self._websocket.add(path, handler)
            return handler

        return decorator

    def add_middleware(
        self,
        mw: Middleware,
        *,
        priority: int | None = None,
        group: str | None = None,
    ) -> None:
        self._middlewares.add(mw, priority=priority, group=group)

    def set_shutdown_policy(self, policy: GracefulShutdownPolicy) -> None:
        self._shutdown_policy = policy

    def set_idempotency_middleware(self, middleware: IdempotencyKeyMiddleware) -> None:
        self._idempotency = middleware

    def set_authorization_core(self, core: AuthorizationCore) -> None:
        self._authz = core

    def set_api_key_manager(self, manager: APIKeyManager) -> None:
        self._api_keys = manager

    def set_security_audit_logger(self, logger: SecurityAuditLogger) -> None:
        self._audit = logger

    def set_cache_backend(self, backend: CacheBackend) -> None:
        self._cache = backend

    def set_cache_invalidation_hooks(self, hooks: CacheInvalidationHooks) -> None:
        self._cache_invalidation = hooks

    def set_canary_routing(self, controls: CanaryRoutingControls) -> None:
        self._canary = controls

    def set_backpressure(self, controller: BackpressureController) -> None:
        self._backpressure = controller

    def set_concurrency_limiter(self, limiter: RouteConcurrencyLimiter) -> None:
        self._concurrency = limiter

    def set_rate_limiter(self, limiter: TokenBucketRateLimiter) -> None:
        self._rate_limiter = limiter

    def set_multi_rate_limiter(self, limiter: MultiKeyRateLimiter) -> None:
        self._multi_rate_limiter = limiter

    def set_http_client(self, client: AsyncHttpClient) -> None:
        self._http_client = client

    def set_etag_manager(self, manager: ETagManager) -> None:
        self._etag = manager

    def set_jwt_auth_guard(self, guard: JWTAuthGuard) -> None:
        self._jwt = guard

    def set_job_runtime(self, jobs: JobRuntime) -> None:
        self._jobs = jobs

    def set_cron_scheduler(self, scheduler: CronScheduler) -> None:
        self._cron = scheduler

    def set_command_bus(self, command_bus: CommandBus) -> None:
        self._command_bus = command_bus

    def set_query_bus(self, query_bus: QueryBus) -> None:
        self._query_bus = query_bus

    def set_http2_stream_manager(self, manager: Http2StreamManager) -> None:
        self._http2_streams = manager

    def set_grpc_gateway(self, gateway: GrpcGateway) -> None:
        self._grpc_gateway = gateway

    def set_multipart_upload(self, stream: MultipartUploadStream) -> None:
        self._multipart_upload = stream

    def set_multipart_parser(self, parser: MultipartParser) -> None:
        self._multipart_parser = parser

    def set_migration_runner(self, runner: MigrationRunner) -> None:
        self._migrations = runner

    def set_content_negotiator(self, negotiator: ContentNegotiator) -> None:
        self._negotiator = negotiator

    def set_oauth2_oidc_helper(self, helper: OAuth2OIDCHelper) -> None:
        self._oauth2 = helper

    def set_outbox_helper(self, helper: OutboxPatternHelper) -> None:
        self._outbox = helper

    def set_static_files(self, service: StaticFileService) -> None:
        self._static_files = service

    def set_sql_adapter(self, adapter: AsyncSQLAdapter) -> None:
        self._sql = adapter

    def set_sql_policy(self, policy: QueryExecutionPolicy) -> None:
        self._sql_policy = policy

    def set_schema_drift_detector(self, detector: SchemaDriftDetector) -> None:
        self._schema_drift = detector

    def set_response_compressor(self, compressor: ResponseCompressor) -> None:
        self._compression = compressor

    def set_cors_profile(self, profile: CORSProfile) -> None:
        self._cors = profile

    def set_csrf_protector(self, protector: CSRFProtector) -> None:
        self._csrf = protector

    def set_db_pool_manager(self, manager: DBConnectionPoolManager) -> None:
        self._db_pools = manager

    def set_dead_letter_queue(self, queue: DeadLetterQueue) -> None:
        self._dead_letter_queue = queue
        self._job_retry.dead_letter_queue = queue

    def set_job_retry_executor(self, executor: JobRetryExecutor) -> None:
        self._job_retry = executor

    def set_event_bus(self, bus: InternalEventBus) -> None:
        self._event_bus = bus

    def set_feature_flags(self, engine: FeatureFlagEngine) -> None:
        self._feature_flags = engine

    def set_secrets_manager(self, manager: SecretsManager) -> None:
        self._secrets = manager

    def set_response_cache_service(self, service: ResponseCacheService) -> None:
        self._response_cache = service

    def set_saga_orchestrator(self, saga: SagaOrchestrator) -> None:
        self._saga = saga

    def set_outbound_circuit_breaker(self, breaker: OutboundCircuitBreaker) -> None:
        self._outbound_circuit_breaker = breaker

    def set_outbound_bulkhead(self, bulkhead: OutboundBulkhead) -> None:
        self._outbound_bulkhead = bulkhead

    def set_retry_policy(self, policy: RetryPolicy) -> None:
        self._retry_policy = policy

    def set_tenant_isolation(self, isolation: TenantIsolationModel) -> None:
        self._tenant_isolation = isolation

    def set_tenant_routing_config(self, config: TenantRoutingConfig) -> None:
        self._tenant_routing = config

    def set_timeout_budget(self, budget: TimeoutBudget) -> None:
        self._timeout_budget = budget

    def set_transaction_scope(self, scope: TransactionScope) -> None:
        self._transaction = scope

    def run(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        workers: int = DEFAULT_WORKERS,
    ) -> None:
        compiled_plan = self._router.compile()
        run_native_server(host, port, max(workers, 1), compiled_plan)
