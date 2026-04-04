"""Locust terhelésteszt a backend REST API végpontjaihoz."""

import io
import random
import string

from locust import HttpUser, between, task


class PhotoAlbumUser(HttpUser):
    """Egy virtuális felhasználó backend API hívásokkal."""

    wait_time = between(1, 3)

    def on_start(self):
        self.username = f"lt_{random.randint(100_000, 999_999)}"
        self.password = "LoadTest123!"
        self.auth_token = ""
        self.own_photo_ids: list[int] = []

        # Regisztráció
        self.client.post(
            "/api/register",
            json={"username": self.username, "password": self.password},
            name="/api/register [POST]",
        )

        self._login()

    # ------------------------------------------------------------------
    # Segédmetódusok
    # ------------------------------------------------------------------

    def _login(self) -> None:
        resp = self.client.post(
            "/api/login",
            json={"username": self.username, "password": self.password},
            name="/api/login [POST]",
        )
        if resp.status_code == 200:
            self.auth_token = (resp.json() or {}).get("token", "")
        else:
            self.auth_token = ""

    def _ensure_login(self) -> bool:
        if not self.auth_token:
            self._login()
        return bool(self.auth_token)

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.auth_token}"}

    def _jpeg(self) -> io.BytesIO:
        # Egyszeru, validszeru JPEG fejléc + random adat terhelesteszt célra.
        body = b"\xff\xd8\xff\xe0" + b"JFIF" + b"\x00" * 16 + bytes(random.getrandbits(8) for _ in range(1024)) + b"\xff\xd9"
        return io.BytesIO(body)

    def _random_name(self) -> str:
        name_length = random.randint(1, 40)
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choice(alphabet) for _ in range(name_length))

    def _photo_ids(self, sort: str = "date", order: str = "desc") -> list[int]:
        resp = self.client.get(
            f"/api/photos?sort={sort}&order={order}",
            name=f"/api/photos?sort={sort}&order={order} [pick]",
        )
        if resp.status_code == 200:
            data = resp.json() or {}
            photos = data.get("photos") or []
            return [int(p["id"]) for p in photos if isinstance(p, dict) and "id" in p]
        return []

    def _random_photo_id(self, sort: str = "date", order: str = "desc"):
        photo_ids = self._photo_ids(sort=sort, order=order)
        if photo_ids:
            return random.choice(photo_ids)
        return None

    # ------------------------------------------------------------------
    # Feladatok
    # ------------------------------------------------------------------

    @task(2)
    def list_photos_by_date_desc(self):
        self.client.get(
            "/api/photos?sort=date&order=desc",
            name="/api/photos?sort=date&order=desc",
        )

    @task(2)
    def list_photos_by_date(self):
        self.client.get(
            "/api/photos?sort=date&order=asc",
            name="/api/photos?sort=date&order=asc",
        )

    @task(2)
    def list_photos_by_name_desc(self):
        self.client.get(
            "/api/photos?sort=name&order=desc",
            name="/api/photos?sort=name&order=desc",
        )

    @task(2)
    def list_photos_by_name_asc(self):
        self.client.get(
            "/api/photos?sort=name&order=asc",
            name="/api/photos?sort=name&order=asc",
        )

    @task(3)
    def upload_photo(self):
        if not self._ensure_login():
            return
        resp = self.client.post(
            "/api/photos",
            files={"photo": ("test.jpg", self._jpeg(), "image/jpeg")},
            data={"name": self._random_name()},
            headers=self._auth_headers(),
            name="/api/photos [POST]",
        )
        if resp.status_code == 201:
            photo_id = (resp.json() or {}).get("id")
            if isinstance(photo_id, int):
                self.own_photo_ids.append(photo_id)

    @task(3)
    def view_photo(self):
        photo_id = self._random_photo_id()
        if photo_id is None:
            return
        self.client.get(f"/api/photos/{photo_id}", name="/api/photos/[id]")
        self.client.get(
            f"/api/photos/{photo_id}/image", name="/api/photos/[id]/image"
        )

    @task(1)
    def delete_own_photo(self):
        if not self.own_photo_ids:
            return
        if not self._ensure_login():
            return
        photo_id = self.own_photo_ids.pop(0)
        self.client.delete(
            f"/api/photos/{photo_id}",
            headers=self._auth_headers(),
            name="/api/photos/[id] [DELETE]",
        )

    @task(1)
    def re_login(self):
        self.auth_token = ""
        self._login()
