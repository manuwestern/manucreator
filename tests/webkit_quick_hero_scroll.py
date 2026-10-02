from pathlib import Path
import json

from playwright.sync_api import sync_playwright


URL = "https://subtle-motion-8.preview.emergentagent.com"
OUT_DIR = Path("/app/test_reports/artifacts/iteration_7")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def grab(page):
    return page.evaluate(
        """() => {
          const track = document.querySelector('[data-testid="hero-scroll-track"]');
          const hero = document.querySelector('[data-testid="hero-section"]');
          const services = document.querySelector('[data-testid="services-section"]');
          const canvas = document.querySelector('[data-testid="hero-frame-canvas"]');
          const csTrack = getComputedStyle(track);
          const csHero = getComputedStyle(hero);
          return {
            scrollY: window.scrollY,
            hero_position: csHero.position,
            hero_top_rect: hero.getBoundingClientRect().top,
            track_height: csTrack.height,
            hero_height: csHero.height,
            services_top_rect: services.getBoundingClientRect().top,
            frame: Number(canvas?.dataset?.frame ?? -1),
            targetFrame: Number(canvas?.dataset?.targetFrame ?? -1),
            doc_height: document.documentElement.scrollHeight
          };
        }"""
    )


def main():
    result = {"desktop": {}, "mobile": {}, "checks": []}
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_selector('[data-testid="hero-scroll-track"]', timeout=15000)
        page.evaluate("document.documentElement.style.scrollBehavior='auto'; document.body.style.scrollBehavior='auto';")
        page.wait_for_timeout(1800)

        base = grab(page)
        page.evaluate("window.scrollTo(0, 200)")
        page.wait_for_timeout(2200)
        s200 = grab(page)
        page.evaluate("window.scrollTo(0, 400)")
        page.wait_for_timeout(2200)
        s400 = grab(page)
        page.evaluate("window.scrollTo(0, 150)")
        page.wait_for_timeout(2200)
        s150 = grab(page)
        before_toggle = page.evaluate("document.documentElement.scrollHeight")
        page.click('[data-testid="hero-motion-toggle"]', force=True)
        page.wait_for_timeout(400)
        after_toggle = page.evaluate("document.documentElement.scrollHeight")
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(200)
        page.click('[data-testid="scroll-discover"]', force=True)
        page.wait_for_timeout(900)
        anchor = page.evaluate(
            """() => {
              const services = document.querySelector('#leistungen');
              return {
                hash: window.location.hash,
                services_top_rect: services.getBoundingClientRect().top,
                scrollY: window.scrollY
              };
            }"""
        )

        result["desktop"] = {
            "base": base,
            "scroll_200": s200,
            "scroll_400": s400,
            "reverse_150": s150,
            "doc_height_before_toggle": before_toggle,
            "doc_height_after_toggle": after_toggle,
            "anchor": anchor,
        }

        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_selector('[data-testid="hero-scroll-track"]', timeout=15000)
        page.evaluate("document.documentElement.style.scrollBehavior='auto'; document.body.style.scrollBehavior='auto';")
        page.wait_for_timeout(1800)
        m_base = grab(page)
        page.evaluate("window.scrollTo(0, 180)")
        page.wait_for_timeout(2200)
        m_180 = grab(page)
        result["mobile"] = {"base": m_base, "scroll_180": m_180}

        browser.close()

    checks = []
    checks.append({"name": "hero_position_relative", "pass": result["desktop"]["base"]["hero_position"] == "relative"})
    checks.append({"name": "track_equals_hero_height", "pass": result["desktop"]["base"]["track_height"] == result["desktop"]["base"]["hero_height"]})
    checks.append({"name": "small_scroll_moves_hero", "pass": round(result["desktop"]["scroll_200"]["hero_top_rect"]) == -200})
    checks.append({"name": "small_scroll_advances_frame", "pass": result["desktop"]["scroll_200"]["frame"] > result["desktop"]["base"]["frame"]})
    checks.append({"name": "reverse_scroll_reverses_frame", "pass": result["desktop"]["reverse_150"]["frame"] < result["desktop"]["scroll_400"]["frame"]})
    checks.append({"name": "motion_toggle_keeps_doc_height", "pass": result["desktop"]["doc_height_before_toggle"] == result["desktop"]["doc_height_after_toggle"]})
    checks.append({"name": "leistungen_anchor_reachable", "pass": result["desktop"]["anchor"]["hash"] == "#leistungen" and result["desktop"]["anchor"]["services_top_rect"] < 160})
    checks.append({"name": "mobile_scroll_moves_hero", "pass": round(result["mobile"]["scroll_180"]["hero_top_rect"]) == -180})
    checks.append({"name": "mobile_scroll_advances_frame", "pass": result["mobile"]["scroll_180"]["frame"] > result["mobile"]["base"]["frame"]})
    result["checks"] = checks

    out = OUT_DIR / "webkit_quick_results.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved: {out}")
    for c in checks:
        print(f"{c['name']}: {'PASS' if c['pass'] else 'FAIL'}")


if __name__ == "__main__":
    main()
