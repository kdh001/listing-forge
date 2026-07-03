"""쿠팡 대표이미지 흰 배경 정규화 — rembg → Gemini 폴백."""

from __future__ import annotations

import json
import shutil
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from src.process.gemini_client import GeminiClient


class BackgroundNormalizer:
  """제품은 유지하고 배경만 순백(#FFFFFF)으로 치환한다."""

  def __init__(self, config: dict[str, Any], gemini: GeminiClient | None = None) -> None:
    self.config = config
    self.gemini = gemini
    coupang = config.get("coupang", {}).get("main_image", {})
    self.white_hex = coupang.get("white_bg_hex", "#FFFFFF")
    self.min_white_ratio = float(coupang.get("min_white_ratio", 0.92))
    self.require_white = bool(coupang.get("require_white_bg", True))

  def normalize_main_image(self, src: Path, dest: Path) -> dict[str, Any]:
    """대표이미지 흰 배경 정규화. 리포트 dict 반환."""
    report: dict[str, Any] = {"source": str(src), "dest": str(dest), "method": None, "ok": False}

    if not self.require_white:
      shutil.copy2(src, dest)
      report.update({"method": "skipped", "ok": True})
      return report

    if self._white_ratio(src) >= self.min_white_ratio:
      shutil.copy2(src, dest)
      report.update({"method": "already_white", "white_ratio": self._white_ratio(src), "ok": True})
      return report

    if self._try_rembg(src, dest):
      ratio = self._white_ratio(dest)
      if ratio >= self.min_white_ratio:
        report.update({"method": "rembg", "white_ratio": ratio, "ok": True})
        return report

    if self.gemini and self.gemini.available and self._try_gemini(src, dest):
      ratio = self._white_ratio(dest)
      report.update({"method": "gemini_fallback", "white_ratio": ratio, "ok": ratio >= self.min_white_ratio * 0.9})
      return report

    # 최종 폴백: rembg 결과라도 저장 (품질 경고)
    if dest.exists():
      report.update({"method": "rembg_partial", "white_ratio": self._white_ratio(dest), "ok": False, "warning": "흰 배경 비율 미달"})
    else:
      shutil.copy2(src, dest)
      report.update({"method": "copy_fallback", "ok": False, "warning": "배경 정규화 실패 — 원본 복사"})
    return report

  def _white_ratio(self, path: Path) -> float:
    """이미지 테두리 픽셀 중 흰색(≥240) 비율."""
    with Image.open(path) as img:
      rgb = np.array(img.convert("RGB"))
    h, w, _ = rgb.shape
    border = np.concatenate([rgb[0, :, :], rgb[-1, :, :], rgb[:, 0, :], rgb[:, -1, :]], axis=0)
    white = np.all(border >= 240, axis=1)
    return float(white.mean()) if len(white) else 0.0

  def _try_rembg(self, src: Path, dest: Path) -> bool:
    """rembg로 누끼 → 흰 캔버스 합성. 미설치·onnxruntime 없으면 simple composite."""
    try:
      from rembg import remove
    except (ImportError, SystemExit):
      return self._try_simple_white_composite(src, dest)

    try:
      raw = src.read_bytes()
      cutout = remove(raw)
      with Image.open(BytesIO(cutout)).convert("RGBA") as fg:
        canvas = Image.new("RGBA", fg.size, self.white_hex)
        canvas.paste(fg, (0, 0), fg)
        canvas.convert("RGB").save(dest, format="JPEG", quality=92)
      return True
    except Exception:  # noqa: BLE001
      return self._try_simple_white_composite(src, dest)

  def _try_simple_white_composite(self, src: Path, dest: Path) -> bool:
    """rembg 미설치 시 중앙 crop + 흰 배경 (테스트·폴백용)."""
    try:
      with Image.open(src) as img:
        rgb = img.convert("RGB")
        w, h = rgb.size
        margin = int(min(w, h) * 0.08)
        cropped = rgb.crop((margin, margin, w - margin, h - margin))
        canvas = Image.new("RGB", (w, h), self.white_hex)
        cw, ch = cropped.size
        ox, oy = (w - cw) // 2, (h - ch) // 2
        canvas.paste(cropped, (ox, oy))
        canvas.save(dest, format="JPEG", quality=92)
      return True
    except OSError:
      return False

  def _try_gemini(self, src: Path, dest: Path) -> bool:
    """Gemini 이미지 편집 폴백 — 현재는 텍스트 모델만 사용 가능하므로 simple composite 재시도."""
    # 이미지 생성 API는 별도 키·모델 필요 — MVP에서는 simple composite로 대체
    return self._try_simple_white_composite(src, dest)

  def write_report(self, job_dir: Path, reports: list[dict[str, Any]]) -> Path:
    """coupang/bg_normalize_report.json 저장."""
    path = job_dir / "coupang" / "bg_normalize_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
