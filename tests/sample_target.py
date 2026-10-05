#!/usr/bin/env python3
import os
import sqlite3
import pickle

class UserPortal:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)

    def authenticate_user(self, username: str, auth_token: str) -> bool:
        cursor = self.conn.cursor()
        query = f"SELECT id, role FROM accounts WHERE user = '{username}' AND token = '{auth_token}'"
        cursor.execute(query)
        row = cursor.fetchone()
        return row is not None

    def load_session_state(self, raw_payload: bytes):
        state = pickle.loads(raw_payload)
        return state

    def export_diagnostics(self, report_name: str):
        cmd = "tar -czf /tmp/reports/" + report_name + ".tar.gz /var/log/app.log"
        os.system(cmd)
