from __future__ import annotations

from typing import Any


_REPORTS: list[dict[str, Any]] = []
_NEXT_REPORT_ID = 7001


def create_report(record: dict[str, Any]) -> dict[str, Any]:
	global _NEXT_REPORT_ID
	stored = {"id": _NEXT_REPORT_ID, **record}
	_NEXT_REPORT_ID += 1
	_REPORTS.append(stored)
	return stored


def get_report(report_id: int) -> dict[str, Any] | None:
	for report in _REPORTS:
		if report["id"] == report_id:
			return report
	return None


def list_reports() -> list[dict[str, Any]]:
	return list(_REPORTS)


def update_report(report_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
	for report in _REPORTS:
		if report["id"] == report_id:
			report.update(updates)
			return report
	return None
