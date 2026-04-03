"""논문 원본 응답을 저장하고 조회하는 계층 구현 모듈."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus

from src.shared import AppSettings, get_settings, resolve_host_and_port

try:
    from pymongo import MongoClient
    from pymongo import ReturnDocument
except ModuleNotFoundError:  # pragma: no cover - depends on runtime environment
    MongoClient = None  # type: ignore[assignment]
    ReturnDocument = None  # type: ignore[assignment]


class RawPaperStore:
    """HF Daily Papers 원본 응답을 MongoDB에 저장하는 진입점."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        client: Any = None,
    ) -> None:
        self.settings = settings or get_settings()
        if client is not None:
            self.client = client
            return
        if MongoClient is None:
            raise ModuleNotFoundError("pymongo가 설치되어 있지 않아 RawPaperStore를 초기화할 수 없습니다.")
        self.client = MongoClient(self._build_mongo_uri())
        self._ensure_collection_indexes()
        self._ensure_state_indexes()
        self._ensure_prepare_queue_indexes()

    def save_daily_papers_response(
        self,
        *,
        date: str,
        payload: list[dict[str, Any]] | dict[str, Any],
    ) -> str:
        """원본 응답과 수집 날짜를 저장하고 저장 식별자를 반환한다."""
        collection = self._collection()
        document = {
            "source": "hf_daily_papers",
            "date": date,
            "payload": payload,
            "fetched_count": len(payload) if isinstance(payload, list) else 1,
            "collected_at": datetime.now(timezone.utc),
        }
        collection.replace_one(
            {"source": "hf_daily_papers", "date": date},
            document,
            upsert=True,
        )
        stored = collection.find_one({"source": "hf_daily_papers", "date": date}, {"_id": 1})
        if stored is None:
            raise RuntimeError("MongoDB에 저장한 raw 문서를 다시 조회하지 못했습니다.")
        return str(stored["_id"])

    def load_daily_papers_response(self, *, date: str) -> list[dict[str, Any]]:
        """수집 날짜 기준 최신 원본 payload를 조회한다."""
        collection = self._collection()
        document = collection.find_one({"source": "hf_daily_papers", "date": date}, sort=[("collected_at", -1)])
        if document is None:
            return []
        payload = document.get("payload")
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return [payload]
        return []

    def has_daily_papers_response(self, *, date: str) -> bool:
        """특정 날짜의 HF Daily Papers 원본이 이미 저장돼 있는지 확인한다."""
        collection = self._collection()
        return collection.count_documents({"source": "hf_daily_papers", "date": date}, limit=1) > 0

    def list_daily_papers_dates(
        self,
        *,
        date_gt: str | None = None,
        date_gte: str | None = None,
        date_lte: str | None = None,
        limit: int | None = None,
        ascending: bool = True,
    ) -> list[str]:
        """조건에 맞는 HF Daily Papers raw 날짜 목록을 정렬해 조회한다."""
        collection = self._collection()
        date_filter: dict[str, Any] = {}
        if date_gt:
            date_filter["$gt"] = date_gt
        if date_gte:
            date_filter["$gte"] = date_gte
        if date_lte:
            date_filter["$lte"] = date_lte

        query: dict[str, Any] = {"source": "hf_daily_papers"}
        if date_filter:
            query["date"] = date_filter

        cursor = collection.find(query, {"_id": 0, "date": 1}).sort("date", 1 if ascending else -1)
        if isinstance(limit, int) and limit > 0:
            cursor = cursor.limit(limit)
        return [str(item.get("date")) for item in cursor if item.get("date")]

    def load_pipeline_state(self, *, pipeline: str, name: str = "default") -> dict[str, Any] | None:
        """파이프라인 진행 상태 문서를 읽는다."""
        collection = self._state_collection()
        document = collection.find_one({"pipeline": pipeline, "name": name}, {"_id": 0})
        if document is None:
            return None
        return document

    def save_pipeline_state(
        self,
        *,
        pipeline: str,
        state: dict[str, Any],
        name: str = "default",
    ) -> None:
        """파이프라인 진행 상태 문서를 저장한다."""
        collection = self._state_collection()
        document = {
            "pipeline": pipeline,
            "name": name,
            **state,
            "updated_at": datetime.now(timezone.utc),
        }
        collection.replace_one(
            {"pipeline": pipeline, "name": name},
            document,
            upsert=True,
        )

    def _collection(self) -> Any:
        return self.client[self.settings.mongo_db][self.settings.mongo_daily_papers_collection]

    def _state_collection(self) -> Any:
        return self.client[self.settings.mongo_db][self.settings.mongo_pipeline_state_collection]

    def _prepare_queue_collection(self) -> Any:
        return self.client[self.settings.mongo_db]["prepare_queue"]

    def _ensure_collection_indexes(self) -> None:
        collection = self._collection()

        duplicate_groups = list(
            collection.aggregate(
                [
                    {"$match": {"source": "hf_daily_papers"}},
                    {"$sort": {"source": 1, "date": 1, "collected_at": -1, "_id": -1}},
                    {
                        "$group": {
                            "_id": {"source": "$source", "date": "$date"},
                            "ids": {"$push": "$_id"},
                            "count": {"$sum": 1},
                        }
                    },
                    {"$match": {"count": {"$gt": 1}}},
                ]
            )
        )
        for group in duplicate_groups:
            duplicate_ids = group.get("ids", [])[1:]
            if duplicate_ids:
                collection.delete_many({"_id": {"$in": duplicate_ids}})

        collection.create_index(
            [("source", 1), ("date", 1)],
            unique=True,
            name="uq_source_date",
        )
        collection.create_index(
            [("source", 1), ("collected_at", -1)],
            name="idx_source_collected_at",
        )

    def _ensure_state_indexes(self) -> None:
        collection = self._state_collection()
        collection.create_index(
            [("pipeline", 1), ("name", 1)],
            unique=True,
            name="uq_pipeline_name",
        )

    def _ensure_prepare_queue_indexes(self) -> None:
        collection = self._prepare_queue_collection()
        collection.create_index(
            [("mode", 1), ("date", 1)],
            unique=True,
            name="uq_prepare_mode_date",
        )
        collection.create_index(
            [("mode", 1), ("status", 1), ("date", 1)],
            name="idx_prepare_mode_status_date",
        )

    def enqueue_prepare_job(
        self,
        *,
        date: str,
        mode: str = "auto",
        source: str = "collect",
    ) -> dict[str, Any]:
        """prepare 작업 큐에 날짜 단위 작업을 추가한다."""
        collection = self._prepare_queue_collection()
        now = datetime.now(timezone.utc)
        result = collection.update_one(
            {"mode": mode, "date": date},
            {
                "$setOnInsert": {
                    "mode": mode,
                    "date": date,
                    "source": source,
                    "status": "pending",
                    "attempt_count": 0,
                    "created_at": now,
                },
                "$set": {
                    "updated_at": now,
                },
            },
            upsert=True,
        )
        document = collection.find_one({"mode": mode, "date": date}, {"_id": 1, "mode": 1, "date": 1, "status": 1})
        return {
            "enqueued": bool(result.upserted_id),
            "job_id": str(document.get("_id")) if document else None,
            "mode": mode,
            "date": date,
            "status": (document or {}).get("status"),
        }

    def claim_prepare_job(
        self,
        *,
        mode: str = "auto",
        worker_id: str = "local_prepare_worker",
    ) -> dict[str, Any] | None:
        """대기 상태의 prepare 작업 1건을 선점해 반환한다."""
        collection = self._prepare_queue_collection()
        now = datetime.now(timezone.utc)
        if ReturnDocument is None:  # pragma: no cover
            raise ModuleNotFoundError("pymongo ReturnDocument를 사용할 수 없습니다.")
        document = collection.find_one_and_update(
            {"mode": mode, "status": "pending"},
            {
                "$set": {
                    "status": "processing",
                    "worker_id": worker_id,
                    "claimed_at": now,
                    "updated_at": now,
                },
                "$inc": {"attempt_count": 1},
            },
            sort=[("date", 1)],
            return_document=ReturnDocument.AFTER,
        )
        return document

    def complete_prepare_job(
        self,
        *,
        mode: str,
        date: str,
        result: dict[str, Any] | None = None,
    ) -> None:
        """prepare 작업을 완료 상태로 갱신한다."""
        collection = self._prepare_queue_collection()
        collection.update_one(
            {"mode": mode, "date": date},
            {
                "$set": {
                    "status": "done",
                    "result": result or {},
                    "finished_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

    def fail_prepare_job(
        self,
        *,
        mode: str,
        date: str,
        error: str,
    ) -> None:
        """prepare 작업을 실패 상태로 갱신한다."""
        collection = self._prepare_queue_collection()
        collection.update_one(
            {"mode": mode, "date": date},
            {
                "$set": {
                    "status": "failed",
                    "error": error,
                    "finished_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

    def _build_mongo_uri(self) -> str:
        if not self.settings.mongo_host:
            raise ValueError("MONGO_HOST가 설정되지 않았습니다.")
        if not self.settings.mongo_initdb_root_username or not self.settings.mongo_initdb_root_password:
            raise ValueError("MongoDB 인증 정보가 설정되지 않았습니다.")

        host, port = resolve_host_and_port(self.settings.mongo_host, self.settings.server_mongo_port)
        return (
            "mongodb://"
            f"{quote_plus(self.settings.mongo_initdb_root_username)}:{quote_plus(self.settings.mongo_initdb_root_password)}"
            f"@{host}:{port}/?authSource=admin"
        )
