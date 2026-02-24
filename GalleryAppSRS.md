# SRS – Gallery / PhotoWebApp (PaaS)

**Verzió:** 1.1  
**Dátum:** 2026-02-24  
**Dokumentum típusa:** Software Requirements Specification

## 1. Cél

A projekt célja egy publikus PaaS környezetben futó, skálázható, többrétegű webes fényképalbum alkalmazás létrehozása, amely támogatja a felhasználókezelést és a fényképek alapvető kezelését.

### 1.1 Feladatfázisok (kurzuskövetelmény)

- **1. beadás (jelen SRS elsődleges fókusza):**
  - publikus PaaS környezetben futó fényképalbum alkalmazás,
  - a megadott funkcionális követelmények teljesítése,
  - GitHub integráció és automatikus build indítás.
- **2. beadás (végleges változat):**
  - külön adatbázis-szerverrel működő architektúra,
  - skálázható és többrétegű végleges üzemeltetési kialakítás,
  - rövid dokumentáció és PaaS-os bemutatás a végleges változatról.

## 2. Hatókör

Az alkalmazás lehetővé teszi:
- felhasználói regisztrációt, bejelentkezést, kijelentkezést,
- fényképek feltöltését és törlését (csak bejelentkezve),
- fényképek listázását névvel és feltöltési dátummal,
- listanézet rendezését név vagy dátum szerint,
- képek megjelenítését listaelem kiválasztásával.

## 3. Környezet és megkötések

1. A megoldásnak publikus PaaS-on kell futnia (célplatform: **OpenShift**, alternatíva: AppEngine / Heroku / egyéb).
2. A rendszernek többrétegű architektúrát kell alkalmaznia (minimum: frontend, backend, adattárolás).
3. A végleges alkalmazásnak skálázhatónak kell lennie.
4. A forráskód GitHub-on tárolt.
5. GitHub push/merge eseményre automatikus build indul.
6. A 2. beadásnál külön adatbázis-szerver kötelező.

## 4. Szerepkörök

- **Vendég felhasználó**
  - képek listázása
  - képek megtekintése
- **Regisztrált felhasználó**
  - vendég jogosultságok +
  - kép feltöltése
  - saját kép törlése

## 5. Funkcionális követelmények

### 5.1 Felhasználókezelés
- **FR-01:** A rendszer biztosítson regisztrációt.
- **FR-02:** A rendszer biztosítson bejelentkezést.
- **FR-03:** A rendszer biztosítson kijelentkezést.

### 5.2 Fényképek kezelése
- **FR-04:** A rendszer engedje fénykép feltöltését bejelentkezett felhasználónak.
- **FR-05:** A rendszer engedje fénykép törlését bejelentkezett felhasználónak.
- **FR-06:** Minden fényképhez kötelezően tartozzon:
  - név (max. 40 karakter),
  - feltöltési dátum-idő (`YYYY-MM-DD HH:mm`).
- **FR-07:** A rendszer listázza a fényképeket névvel és dátummal.
- **FR-08:** A lista rendezhető legyen:
  - név szerint,
  - dátum szerint.
- **FR-09:** Listaelem kiválasztásakor a rendszer jelenítse meg a hozzá tartozó képet.
- **FR-10:** Feltöltés és törlés csak hitelesített felhasználó számára legyen elérhető.

### 5.3 Opcionális funkciók
- **FR-11 (opcionális):** Keresés képnév alapján.
- **FR-12 (opcionális):** Lapozás.
- **FR-13 (opcionális):** Képcímkék.

## 6. Nem funkcionális követelmények

### 6.1 Teljesítmény
- **NFR-01:** A listázási válaszidő normál terhelésen átlagosan ≤ 2s.
- **NFR-02:** Képmegjelenítés normál hálózaton ≤ 3s (tipikus képméretig).

### 6.2 Skálázhatóság
- **NFR-03:** Az alkalmazás több példányban futtatható legyen.
- **NFR-04:** A backend stateless kialakítású legyen (alkalmazásállapot ne lokális memóriában tárolódjon).

### 6.3 Biztonság
- **NFR-05:** Jelszavak csak hash-elve tárolhatók.
- **NFR-06:** A kommunikáció HTTPS-en történjen.
- **NFR-07:** Kötelező input validáció (különösen névmező és auth adatok).

### 6.4 Üzemeltetés
- **NFR-08:** Build/deploy folyamat CI/CD-vel automatizált.
- **NFR-09:** Alkalmazásnaplók a PaaS felületen elérhetők.

## 7. Adatkövetelmények (minimum)

### 7.1 User
- `id`
- `username/email` (egyedi)
- `password_hash`
- `created_at`

### 7.2 Photo
- `id`
- `owner_user_id`
- `name` (max 40)
- `upload_datetime`
- `file_path_or_url`

## 8. Üzleti szabályok

- **BR-01:** Képnév hossza 1–40 karakter.
- **BR-02:** Feltöltési dátum kötelező.
- **BR-03:** Törlés csak bejelentkezett felhasználó számára engedélyezett.
- **BR-04:** Nem hitelesített feltöltés/törlés kísérletet a rendszer elutasít.

## 9. Elfogadási kritériumok

### 9.1 Elfogadási kritériumok – 1. beadás

1. Az alkalmazás publikus PaaS URL-en fut (elsődlegesen OpenShift környezetben).
2. GitHub push után automatikus build indul.
3. Regisztráció, bejelentkezés, kijelentkezés működik.
4. Bejelentkezett felhasználó tud feltölteni és törölni.
5. Képlista névvel és dátummal megjelenik, rendezhető (név/dátum szerint).
6. Listaelem kiválasztásakor a kép megjelenik.
7. A 40 karakternél hosszabb képnév elutasításra kerül.

### 9.2 Elfogadási kritériumok – 2. beadás (végleges)

1. Az alkalmazás külön adatbázis-szerverrel működik.
2. Az architektúra többrétegű és skálázható módon üzemeltetett.
3. A backend stateless követelmény teljesül.
4. A teljes funkcionális követelménykészlet működik (feltöltés, törlés, listázás/rendezés, képmegjelenítés, autentikáció).
5. Az alkalmazás publikus PaaS környezetben működés közben bemutatható.

## 10. Benyújtandó elemek (2. beadás)

1. Rövid dokumentáció a végleges megoldásról:
  - választott PaaS környezet,
  - alkalmazásrétegek,
  - rétegek közötti kapcsolatok.
2. A megoldás forrásfájljai GitHub-on, a repository link megadásával.
3. Működő alkalmazás bemutatása a PaaS környezetben.
4. Amennyiben a végleges változat korábban már bemutatásra került, a dokumentáció újbóli feltöltése elegendő.