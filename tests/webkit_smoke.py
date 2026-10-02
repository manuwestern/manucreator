import json
import os
import time
from typing import Any, Dict, Optional

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


URL = "https://subtle-motion-8.preview.emergentagent.com"
ARTIFACT_DIR = "/app/test_reports/artifacts/iteration_6"
RESULT_PATH = f"{ARTIFACT_DIR}/webkit_results.json"


def ensure_dirs() -> None:
    os.makedirs(ARTIFACT_DIR, exist_ok=True)


def capture_state(page, label: str, screenshot_name: str) -> Dict[str, Any]:
    state = page.evaluate(
        """() => {
        const track = document.querySelector('[data-testid="hero-scroll-track"]');
        const stage = document.querySelector('[data-testid="hero-video-stage"]');
        const canvas = document.querySelector('[data-testid="hero-frame-canvas"]');
        const rect = track ? track.getBoundingClientRect() : null;
        const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
        let hash = null;
        let avg = null;
        if (canvas) {
          const ctx = canvas.getContext('2d', { willReadFrequently: true });
          if (ctx) {
            const w = Math.max(1, Math.floor(canvas.width / 12));
            const h = Math.max(1, Math.floor(canvas.height / 12));
            const data = ctx.getImageData(0, 0, w, h).data;
            let rolling = 0;
            let total = 0;
            for (let i = 0; i < data.length; i += 4) {
              const lum = data[i] + data[i + 1] + data[i + 2];
              total += lum;
              rolling = (rolling * 131 + lum + i) % 1000000007;
            }
            hash = String(rolling);
            avg = Number((total / Math.max(1, data.length / 4)).toFixed(2));
          }
        }
        return {
          hasCanvas: !!canvas,
          frame: canvas ? canvas.dataset.frame ?? null : null,
          targetFrame: canvas ? canvas.dataset.targetFrame ?? null : null,
          stageState: stage ? stage.dataset.state ?? null : null,
          scrollY: Math.round(window.scrollY),
          scrollHeight: document.documentElement.scrollHeight,
          viewportHeight: window.innerHeight,
          maxScroll,
          trackTop: rect ? Math.round(rect.top) : null,
          trackHeight: rect ? Math.round(rect.height) : null,
          canvasHash: hash,
          canvasAvgLum: avg,
        };
      }"""
    )
    page.screenshot(path=f"{ARTIFACT_DIR}/{screenshot_name}", quality=40, full_page=False)
    state["label"] = label
    state["screenshot"] = f"{ARTIFACT_DIR}/{screenshot_name}"
    print(f"{label}: {json.dumps(state, ensure_ascii=False)}")
    return state


def wait_for_canvas_ready(page, timeout_ms: int = 15000) -> None:
    page.wait_for_selector('[data-testid="hero-scroll-track"]', timeout=timeout_ms)
    page.wait_for_selector('[data-testid="hero-video-stage"]', timeout=timeout_ms)
    page.wait_for_function(
        """() => {
        const stage = document.querySelector('[data-testid="hero-video-stage"]');
        const canvas = document.querySelector('[data-testid="hero-frame-canvas"]');
        return !!stage && (!!canvas || stage.dataset.state === 'static');
      }""",
        timeout=timeout_ms,
    )


def scroll_track_percent(page, ratio: float) -> None:
    page.evaluate(
        """(r) => {
        const track = document.querySelector('[data-testid="hero-scroll-track"]');
        if (!track) return;
        const doc = document.documentElement;
        const maxScroll = Math.max(1, doc.scrollHeight - window.innerHeight);
        const rect = track.getBoundingClientRect();
        const top = window.scrollY + rect.top;
        const target = Math.max(0, Math.min(maxScroll, top + rect.height * r));
        window.scrollTo(0, target);
      }""",
        ratio,
    )


def wait_frame_settle(page, min_wait_ms: int = 1200, timeout_ms: int = 8000) -> None:
    deadline = time.time() + (timeout_ms / 1000)
    last_frame = None
    stable_since = time.time()
    while time.time() < deadline:
        frame = page.get_attribute('[data-testid="hero-frame-canvas"]', "data-frame")
        if frame == last_frame:
            if (time.time() - stable_since) * 1000 >= min_wait_ms:
                return
        else:
            last_frame = frame
            stable_since = time.time()
        page.wait_for_timeout(150)
    page.wait_for_timeout(min_wait_ms)


def run_directional_frame_test(context, device_name: str, viewport: Dict[str, int]) -> Dict[str, Any]:
    page = context.new_page()
    page.set_viewport_size(viewport)
    page.goto(URL, wait_until="domcontentloaded", timeout=45000)
    wait_for_canvas_ready(page)
    page.wait_for_timeout(1200)

    states = []
    states.append(capture_state(page, f"{device_name}_start", f"{device_name}_start.jpeg"))

    scroll_track_percent(page, 0.5)
    wait_frame_settle(page)
    middle_state = capture_state(page, f"{device_name}_middle", f"{device_name}_middle.jpeg")
    states.append(middle_state)
    if middle_state.get("frame") != middle_state.get("targetFrame"):
        page.wait_for_timeout(5000)
        states.append(capture_state(page, f"{device_name}_middle_late", f"{device_name}_middle_late.jpeg"))

    scroll_track_percent(page, 1.0)
    wait_frame_settle(page)
    states.append(capture_state(page, f"{device_name}_end", f"{device_name}_end.jpeg"))

    scroll_track_percent(page, 0.0)
    wait_frame_settle(page)
    states.append(capture_state(page, f"{device_name}_reverse_start", f"{device_name}_reverse_start.jpeg"))

    page.wait_for_timeout(1800)
    states.append(capture_state(page, f"{device_name}_idle_settle", f"{device_name}_idle_settle.jpeg"))

    page.close()
    return {
        "device": device_name,
        "viewport": viewport,
        "states": states,
    }


def run_concurrency_test(context) -> Dict[str, Any]:
    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 800})

    active = set()
    peak_active = 0
    requests_seen = 0
    lifecycle_log = []
    crashed = {"value": False}

    def is_seq(req) -> bool:
        return "/media/hero-sequence/" in req.url

    def on_request(req):
        nonlocal peak_active, requests_seen
        if not is_seq(req):
            return
        requests_seen += 1
        rid = id(req)
        active.add(rid)
        peak_active = max(peak_active, len(active))
        lifecycle_log.append({"event": "request", "active": len(active), "url": req.url})

    def on_finished(req):
        if not is_seq(req):
            return
        active.discard(id(req))
        lifecycle_log.append({"event": "finished", "active": len(active), "url": req.url})

    def on_failed(req):
        if not is_seq(req):
            return
        active.discard(id(req))
        lifecycle_log.append({"event": "failed", "active": len(active), "url": req.url, "failure": req.failure})

    page.on("request", on_request)
    page.on("requestfinished", on_finished)
    page.on("requestfailed", on_failed)
    page.on("crash", lambda: crashed.__setitem__("value", True))

    def delayed_continue(route):
        time.sleep(1.2)
        route.continue_()

    page.route("**/media/hero-sequence/**", delayed_continue)

    page.goto(URL, wait_until="domcontentloaded", timeout=45000)
    wait_for_canvas_ready(page)
    page.wait_for_timeout(1000)

    # Rapid direction flips to stress loader scheduling
    for _ in range(2):
        page.mouse.wheel(0, 1800)
        page.wait_for_timeout(220)
        page.mouse.wheel(0, -1700)
        page.wait_for_timeout(220)

    # Off/on quickly to test overlapping loader cleanup
    motion_toggle = page.locator('[data-testid="hero-motion-toggle"]')
    motion_toggle.click(force=True)
    page.wait_for_timeout(200)
    motion_toggle.click(force=True)

    page.wait_for_timeout(3600)
    if page.is_closed():
        raise RuntimeError("WebKit page closed during delayed routing stress")
    final_state = capture_state(page, "concurrency_final", "concurrency_final.jpeg")

    drained = False
    for _ in range(40):
        if len(active) == 0:
            drained = True
            break
        page.wait_for_timeout(200)

    page.unroute("**/media/hero-sequence/**")
    page.wait_for_timeout(700)
    page.close()
    return {
        "requests_seen": requests_seen,
        "peak_active": peak_active,
        "active_end": len(active),
        "drained_before_close": drained,
        "page_crashed": crashed["value"],
        "lifecycle_tail": lifecycle_log[-30:],
        "final_state": final_state,
        "pass_cap_le_3": peak_active <= 3,
    }


def run_failure_retry_test(context) -> Dict[str, Any]:
    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 800})
    page.route("**/media/hero-sequence/**", lambda route: route.abort())
    page.goto(URL, wait_until="domcontentloaded", timeout=45000)
    wait_for_canvas_ready(page)

    page.wait_for_function(
        """() => {
        const btn = document.querySelector('[data-testid="hero-motion-toggle"]');
        if (!btn) return false;
        return ((btn.getAttribute('aria-label') || '').toLowerCase().includes('erneut'));
      }""",
        timeout=15000,
    )
    failed_state = capture_state(page, "failure_state", "failure_state.jpeg")

    page.unroute("**/media/hero-sequence/**")
    toggle = page.locator('[data-testid="hero-motion-toggle"]')
    toggle.click(force=True)
    page.wait_for_timeout(200)

    page.wait_for_selector('[data-testid="hero-frame-canvas"]', timeout=15000)
    page.wait_for_timeout(1600)
    recovered_state = capture_state(page, "retry_recovered", "retry_recovered.jpeg")

    page.close()
    return {
        "failed_state": failed_state,
        "recovered_state": recovered_state,
    }


def run_reduced_motion_opt_in_test(browser) -> Dict[str, Any]:
    context = browser.new_context(reduced_motion="reduce")
    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 800})
    page.goto(URL, wait_until="domcontentloaded", timeout=45000)
    wait_for_canvas_ready(page)
    page.wait_for_timeout(600)

    static_state = capture_state(page, "reduced_static", "reduced_static.jpeg")
    toggle = page.locator('[data-testid="hero-motion-toggle"]')
    toggle.click(force=True)

    page.wait_for_selector('[data-testid="hero-frame-canvas"]', timeout=15000)
    page.wait_for_timeout(1800)
    opted_in_state = capture_state(page, "reduced_opted_in", "reduced_opted_in.jpeg")

    page.close()
    context.close()
    return {
        "static_state": static_state,
        "opted_in_state": opted_in_state,
    }


def safe_run(label: str, fn):
    try:
        return {"ok": True, "result": fn()}
    except PlaywrightTimeoutError as exc:
        print(f"{label} timeout: {exc}")
        return {"ok": False, "error": f"timeout: {exc}"}
    except Exception as exc:  # broad catch to keep subsequent checks running
        print(f"{label} error: {exc}")
        return {"ok": False, "error": str(exc)}


def main():
    ensure_dirs()
    payload: Dict[str, Any] = {"url": URL, "timestamp": time.time(), "engine": "webkit"}
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=True)
        context = browser.new_context()

        payload["desktop_directional"] = safe_run(
            "desktop_directional",
            lambda: run_directional_frame_test(context, "desktop_1920x800", {"width": 1920, "height": 800}),
        )
        payload["mobile_directional"] = safe_run(
            "mobile_directional",
            lambda: run_directional_frame_test(context, "mobile_390x844", {"width": 390, "height": 844}),
        )
        payload["concurrency_stress"] = safe_run("concurrency_stress", lambda: run_concurrency_test(context))
        payload["failure_retry"] = safe_run("failure_retry", lambda: run_failure_retry_test(context))
        payload["reduced_motion_opt_in"] = safe_run(
            "reduced_motion_opt_in", lambda: run_reduced_motion_opt_in_test(browser)
        )

        context.close()
        browser.close()

    with open(RESULT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    print(f"Wrote results: {RESULT_PATH}")


if __name__ == "__main__":
    main()
