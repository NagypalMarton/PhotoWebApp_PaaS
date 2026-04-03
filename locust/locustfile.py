"""
Locust terhelésteszt – Fényképalbum alkalmazás
===============================================
Lefedett funkciók:
  - Regisztráció / bejelentkezés
  - Fotólista lekérése (dátum és név szerinti rendezéssel)
  - Fotó feltöltése
  - Fotó megtekintése (metaadatok + képfájl)
  - Fotó törlése
"""

import io
import re
import random
import string
from typing import Optional

from locust import HttpUser, between, task

class PhotoAlbumUser(HttpUser):
    """
    Egy virtuális felhasználó szimulációja:
            1. Regisztráció a frontend felületen (on_start)
            2. Bejelentkezés a frontend felületen (on_start)
            3. 5-25 kép letöltése a Picsumról (on_start)
            4. Vegyesen: rendezés, feltöltés, megtekintés, törlés, kijelentkezés

    Kérések aránya:
            list_by_date_desc   : 2
            list_by_date_asc    : 2
            list_by_name_desc   : 2
            list_by_name_asc    : 2
            view_photo          : 3
            upload_photo        : 3
            delete_photo        : 1
            logout              : 1
    """

    wait_time = between(1, 3)

    def on_start(self):
        self.username = f"lt_{random.randint(100_000, 999_999)}"
        self.password = "LoadTest123!"
        self.frontend_logged_in = False
        self.own_photo_ids: list[int] = []
        self.upload_images: list[bytes] = []

        # Regisztráció – ha már létezik, nem probléma
        self.client.post(
            "/register",
            data={"username": self.username, "password": self.password},
            name="/register [POST]",
        )

        # Bejelentkezés
        resp = self.client.post(
            "/login",
            data={"username": self.username, "password": self.password},
            name="/login [POST]",
        )
        self.frontend_logged_in = resp.status_code in (200, 302)

        self.upload_images = self._download_upload_images()

    # ------------------------------------------------------------------
    # Segédmetódusok
    # ------------------------------------------------------------------

    def _frontend_login(self) -> None:
        resp = self.client.post(
            "/login",
            data={"username": self.username, "password": self.password},
            name="/login [POST]",
        )
        self.frontend_logged_in = resp.status_code in (200, 302)

    def _ensure_frontend_login(self) -> None:
        if not self.frontend_logged_in:
            self._frontend_login()

    def _jpeg(self) -> io.BytesIO:
        if self.upload_images:
            return io.BytesIO(random.choice(self.upload_images))
        return io.BytesIO()

    def _download_upload_images(self) -> list[bytes]:
        images: list[bytes] = []
        image_count = random.randint(5, 25)

        for _ in range(image_count):
            cache_buster = random.randint(1, 1_000_000_000)
            resp = self.client.get(
                f"https://picsum.photos/200?cachebust={cache_buster}",
                name="https://picsum.photos/200 [download]",
                allow_redirects=True,
            )
            if resp.status_code == 200 and resp.content:
                images.append(resp.content)

        return images

    def _random_name(self) -> str:
        name_length = random.randint(1, 40)
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choice(alphabet) for _ in range(name_length))

    def _photo_ids_from_index(self, sort: str = "date", order: str = "desc") -> list[int]:
        """Visszaadja a frontend index oldalon látható fotó ID-kat."""
        resp = self.client.get(
            f"/?sort={sort}&order={order}",
            name=f"/?sort={sort}&order={order} [pick]",
        )
        if resp.status_code == 200:
            return [int(match) for match in re.findall(r'href="/photo/(\d+)"', resp.text)]
        return []

    def _random_photo_id(self, sort: str = "date", order: str = "desc") -> Optional[int]:
        photo_ids = self._photo_ids_from_index(sort=sort, order=order)
        if photo_ids:
            return random.choice(photo_ids)
        return None

    # ------------------------------------------------------------------
    # Feladatok
    # ------------------------------------------------------------------

    @task(2)
    def list_photos_by_date_desc(self):
        """GET /?sort=date&order=desc – fotólista dátum szerint, csökkenő sorrendben"""
        self.client.get("/?sort=date&order=desc", name="/?sort=date&order=desc")

    @task(2)
    def list_photos_by_date(self):
        """GET /?sort=date&order=asc – fotólista dátum szerint, növekvő sorrendben"""
        self.client.get("/?sort=date&order=asc", name="/?sort=date&order=asc")

    @task(2)
    def list_photos_by_name_desc(self):
        """GET /?sort=name&order=desc – fotólista név szerint, csökkenő sorrendben"""
        self.client.get("/?sort=name&order=desc", name="/?sort=name&order=desc")

    @task(2)
    def list_photos_by_name_asc(self):
        """GET /?sort=name&order=asc – fotólista név szerint, növekvő sorrendben"""
        self.client.get("/?sort=name&order=asc", name="/?sort=name&order=asc")

    @task(3)
    def upload_photo(self):
        """POST /upload – fotó feltöltése a frontend űrlapon keresztül"""
        if not self.frontend_logged_in:
            return
        if not self.upload_images:
            return
        resp = self.client.post(
            "/upload",
            files={"photo": ("test.jpg", self._jpeg(), "image/jpeg")},
            data={"name": self._random_name()},
            name="/upload [POST]",
        )
        if resp.status_code in (200, 302):
            photo_id = self._random_photo_id(sort="date", order="desc")
            if photo_id:
                self.own_photo_ids.append(photo_id)

    @task(3)
    def view_photo(self):
        """GET /photo/<id> + GET /photo/<id>/image – fotó megtekintése"""
        photo_id = self._random_photo_id()
        if photo_id is None:
            return
        self.client.get(f"/photo/{photo_id}", name="/photo/[id]")
        self.client.get(
            f"/photo/{photo_id}/image", name="/photo/[id]/image"
        )

    @task(1)
    def delete_own_photo(self):
        """POST /delete/<id> – saját fotó törlése a frontend felületen"""
        if not self.frontend_logged_in or not self.own_photo_ids:
            return
        photo_id = self.own_photo_ids.pop(0)
        self.client.post(
            f"/delete/{photo_id}",
            name="/delete/[id] [POST]",
        )

    @task(1)
    def logout(self):
        """GET /logout – kijelentkezés, majd újrabejelentkezés a frontend sessionhöz"""
        if not self.frontend_logged_in:
            return
        self.client.get("/logout", name="/logout")
        self.frontend_logged_in = False
        self._frontend_login()
