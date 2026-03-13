from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass
class Topic:
    id: str
    title_hint: str
    angle: str
    target_reader: str
    keywords: list[str]
    must_include: str
    priority: int
    status: str
    scheduled_date: str


class TopicQueue:
    def __init__(self, csv_path: Path) -> None:
        self.csv_path = csv_path

    def load_all(self) -> list[Topic]:
        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = []
            for row in reader:
                rows.append(
                    Topic(
                        id=row["id"],
                        title_hint=row["title_hint"],
                        angle=row["angle"],
                        target_reader=row["target_reader"],
                        keywords=[keyword.strip() for keyword in row["keywords"].split(",") if keyword.strip()],
                        must_include=row["must_include"],
                        priority=int(row["priority"] or "999"),
                        status=row["status"],
                        scheduled_date=row["scheduled_date"],
                    )
                )
        return rows

    def list_pending(self) -> list[Topic]:
        today = date.today().isoformat()
        topics = [
            topic
            for topic in self.load_all()
            if topic.status == "pending" and (not topic.scheduled_date or topic.scheduled_date <= today)
        ]
        return sorted(topics, key=lambda topic: (topic.priority, topic.id))

    def get_by_id(self, topic_id: str) -> Topic:
        for topic in self.load_all():
            if topic.id == topic_id:
                return topic
        raise ValueError(f"Topic not found: {topic_id}")

    def next_topic(self) -> Topic:
        pending = self.list_pending()
        if not pending:
            raise ValueError("No pending topic is available.")
        return pending[0]

    def update_status(self, topic_id: str, new_status: str) -> None:
        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            rows = list(reader)

        updated = False
        for row in rows:
            if row["id"] == topic_id:
                row["status"] = new_status
                updated = True
                break

        if not updated:
            raise ValueError(f"Topic not found: {topic_id}")

        with self.csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

