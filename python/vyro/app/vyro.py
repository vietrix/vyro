from __future__ import annotations

from typing import Any, Callable

from vyro.middleware import Middleware
from vyro.middleware.idempotency import IdempotencyKeyMiddleware
from vyro.middleware.registry import MiddlewareRegistry
from vyro.routing.registry import RouterRegistry
from vyro.runtime.async_ops.cron import CronScheduler
from vyro.runtime.async_ops.dead_letter import DeadLetterQueue, JobRetryExecutor
from vyro.runtime.async_ops.event_bus import InternalEventBus
from vyro.runtime.async_ops.jobs import JobRuntime
from vyro.runtime.async_ops.saga import SagaOrchestrator
from vyro.runtime.data.cqrs import CommandBus, QueryBus
from vyro.runtime.data.db_pool import DBConnectionPoolManager
from vyro.runtime.data.migrations import MigrationRunner
from vyro.runtime.data.outbox import OutboxPatternHelper
from vyro.runtime.data.schema_drift import SchemaDriftDetector
from vyro.runtime.data.sql import AsyncSQLAdapter, SQLiteAsyncAdapter
from vyro.runtime.data.sql_policy import QueryExecutionPolicy
from vyro.runtime.data.transaction import TransactionScope
from vyro.runtime.edge.compression import ResponseCompressor
from vyro.runtime.edge.etag import ETagManager
from vyro.runtime.edge.grpc_gateway import GrpcGateway
from vyro.runtime.edge.http_client import AsyncHttpClient
from vyro.runtime.edge.http2 import Http2StreamManager
from vyro.runtime.edge.multipart_parser import MultipartParser
from vyro.runtime.edge.multipart_upload import MultipartUploadStream
from vyro.runtime.edge.negotiation import ContentNegotiator
from vyro.runtime.edge.static_files import StaticFileService
from vyro.runtime.edge.websocket import WebSocketRouteRegistry
from vyro.runtime.platform.blue_green import BlueGreenRolloutHelper
from vyro.runtime.platform.cache import CacheBackend, MemoryCacheBackend
from vyro.runtime.platform.cache_invalidation import CacheInvalidationHooks
from vyro.runtime.platform.canary import CanaryRoutingControls
from vyro.runtime.platform.discovery import ServiceDiscoveryRegistry
from vyro.runtime.platform.feature_flags import FeatureFlagEngine
from vyro.runtime.platform.hot_reload import SafeRuntimeConfigReloader
from vyro.runtime.platform.kubernetes import KubernetesManifestGenerator
from vyro.runtime.platform.marketplace import ExtensionMarketplaceManifest
from vyro.runtime.platform.nogil import NoGILWorkerTuner
from vyro.runtime.platform.plugins import ABIStablePluginSystem
from vyro.runtime.platform.response_cache import ResponseCacheService
from vyro.runtime.resilience.backpressure import BackpressureController
from vyro.runtime.resilience.bulkhead import OutboundBulkhead
from vyro.runtime.resilience.circuit_breaker import OutboundCircuitBreaker
from vyro.runtime.resilience.concurrency import RouteConcurrencyLimiter
from vyro.runtime.resilience.rate_limit import MultiKeyRateLimiter, TokenBucketRateLimiter
from vyro.runtime.resilience.retry import RetryPolicy
from vyro.runtime.resilience.timeout_budget import TimeoutBudget
from vyro.runtime.security.api_keys import APIKeyManager
from vyro.runtime.security.audit import SecurityAuditLogger
from vyro.runtime.security.authorization import AuthorizationCore
from vyro.runtime.security.cors import CORSProfile
from vyro.runtime.security.csrf import CSRFProtector
from vyro.runtime.security.jwt_auth import JWTAuthGuard
from vyro.runtime.security.oauth2_oidc import OAUTH2_DEFAULT_CONFIG, OAuth2OIDCHelper
from vyro.runtime.security.secrets import SecretsManager
from vyro.runtime.security.tenant import TenantIsolationModel
from vyro.runtime.security.tenant_routing import TenantRoutingConfig
from vyro.runtime.server import run_native_server
from vyro.runtime.shutdown import GracefulShutdownPolicy
from vyro.settings import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_WORKERS
from vyro.app.container import build_default_components


class Vyro:
    def __init__(self) -> None:
        components = build_default_components()
        self._router = RouterRegistry()
        self._middlewares = MiddlewareRegistry()
        self._idempotency = components["idempotency"]
        self._authz = components["authz"]
        self._api_keys = components["api_keys"]
        self._audit = components["audit"]
        self._cache = components["cache"]
        self._cache_invalidation = components["cache_invalidation"]
        self._blue_green = components["blue_green"]
        self._canary = components["canary"]
        self._shutdown_policy = components["shutdown_policy"]
        self._backpressure = components["backpressure"]
        self._concurrency = components["concurrency"]
        self._rate_limiter = components["rate_limiter"]
        self._multi_rate_limiter = components["multi_rate_limiter"]
        self._http_client = components["http_client"]
        self._etag = components["etag"]
        self._jwt = components["jwt"]
        self._jobs = components["jobs"]
        self._cron = components["cron"]
        self._command_bus = components["command_bus"]
        self._query_bus = components["query_bus"]
        self._http2_streams = components["http2_streams"]
        self._grpc_gateway = components["grpc_gateway"]
        self._multipart_upload = components["multipart_upload"]
        self._multipart_parser = components["multipart_parser"]
        self._migrations = components["migrations"]
        self._marketplace = components["marketplace"]
        self._hot_reload = components["hot_reload"]
        self._nogil_tuner = components["nogil_tuner"]
        self._k8s_generator = components["k8s_generator"]
        self._negotiator = components["negotiator"]
        self._oauth2 = components["oauth2"]
        self._outbox = components["outbox"]
        self._plugins = components["plugins"]
        self._static_files = components["static_files"]
        self._sql = components["sql"]
        self._sql_policy = components["sql_policy"]
        self._schema_drift = components["schema_drift"]
        self._compression = components["compression"]
        self._cors = components["cors"]
        self._csrf = components["csrf"]
        self._db_pools = components["db_pools"]
        self._dead_letter_queue = components["dead_letter_queue"]
        self._job_retry = components["job_retry"]
        self._discovery = components["discovery"]
        self._event_bus = components["event_bus"]
        self._feature_flags = components["feature_flags"]
        self._secrets = components["secrets"]
        self._response_cache = components["response_cache"]
        self._saga = components["saga"]
        self._outbound_circuit_breaker = components["circuit_breaker"]
        self._outbound_bulkhead = components["bulkhead"]
        self._retry_policy = components["retry_policy"]
        self._tenant_isolation = components["tenant_isolation"]
        self._tenant_routing = components["tenant_routing"]
        self._timeout_budget = components["timeout_budget"]
        self._transaction = components["transaction"]
        self._websocket = components["websocket"]

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

    def set_blue_green_rollout(self, helper: BlueGreenRolloutHelper) -> None:
        self._blue_green = helper

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

    def set_extension_marketplace(self, marketplace: ExtensionMarketplaceManifest) -> None:
        self._marketplace = marketplace

    def set_runtime_config_reloader(self, reloader: SafeRuntimeConfigReloader) -> None:
        self._hot_reload = reloader

    def set_no_gil_tuner(self, tuner: NoGILWorkerTuner) -> None:
        self._nogil_tuner = tuner

    def set_kubernetes_manifest_generator(self, generator: KubernetesManifestGenerator) -> None:
        self._k8s_generator = generator

    def set_content_negotiator(self, negotiator: ContentNegotiator) -> None:
        self._negotiator = negotiator

    def set_oauth2_oidc_helper(self, helper: OAuth2OIDCHelper) -> None:
        self._oauth2 = helper

    def set_outbox_helper(self, helper: OutboxPatternHelper) -> None:
        self._outbox = helper

    def set_plugin_system(self, plugins: ABIStablePluginSystem) -> None:
        self._plugins = plugins

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

    def set_service_discovery(self, discovery: ServiceDiscoveryRegistry) -> None:
        self._discovery = discovery

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
