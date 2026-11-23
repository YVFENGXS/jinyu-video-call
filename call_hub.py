# -*- coding: utf-8 -*-
"""通话舞台的 WebSocket 集线器：一个舞台，多端订阅。

角色：
- viewer  通话页面（可发文字、收舞台指令）
- panel   只读面板（跟随表情/动作，不说话）
- pet     桌宠（只接收 say / stage，不说话）

设计约束：
- 纯内存，单进程；不做持久化，不保存对话内容；
- 广播失败就断开该连接，绝不影响主流程；
- 协议很薄：所有消息都是 JSON，带 `type`，其余字段原样透传。
"""
from __future__ import annotations

import time

ROLES = ("viewer", "panel", "pet")


class Hub:
    def __init__(self):
        self._clients = {}

    def add(self, ws, role: str = "viewer", session: str = "") -> None:
        role = role if role in ROLES else "viewer"
        self._clients[id(ws)] = {
            "ws": ws, "role": role, "session": str(session or "")[:64],
            "since": time.time(),
        }

    def drop(self, ws) -> None:
        self._clients.pop(id(ws), None)

    def presence(self) -> dict:
        roles = {}
        sessions = set()
        for item in self._clients.values():
            roles[item["role"]] = roles.get(item["role"], 0) + 1
            if item["session"]:
                sessions.add(item["session"])
        return {"total": len(self._clients), "roles": roles,
                "sessions": sorted(sessions)}

    async def send(self, ws, payload: dict) -> bool:
        try:
            await ws.send_json(payload)
            return True
        except Exception:
            self.drop(ws)
            return False

    async def broadcast(self, payload: dict, roles=None, exclude=None,
                        session=None) -> int:
        """向指定角色/会话广播；返回成功送达的连接数。"""
        wanted = set(roles) if roles else None
        sent = 0
        for item in list(self._clients.values()):
            if exclude is not None and item["ws"] is exclude:
                continue
            if wanted and item["role"] not in wanted:
                continue
            if session and item["session"] and item["session"] != str(session):
                continue
            if await self.send(item["ws"], payload):
                sent += 1
        return sent
