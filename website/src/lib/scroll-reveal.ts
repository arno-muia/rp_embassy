/**
 * ScrollReveal — Astro-native motion infrastructure
 *
 * Migrated from apps/web to replace GSAP `ScrollTrigger` + framer-motion
 * `whileInView` / `useScrollReveal`. No React, no GSAP — uses
 * IntersectionObserver + CSS transitions.
 *
 * Source behavior preserved:
 *   - y offset (default 30)
 *   - opacity fade (default 0)
 *   - duration (default 0.6s)
 *   - stagger support (per-child delay)
 *   - delay support
 *   - threshold support
 *   - start position (e.g. "top 85%") mapped to IntersectionObserver rootMargin
 *   - easing (source used GSAP "power3.out" -> cubic-bezier(0.215,0.61,0.355,1))
 *   - prefers-reduced-motion: content is shown immediately, no transition
 *
 * Usage in Astro components:
 *   <section data-reveal data-reveal-stagger="0.1" data-reveal-y="24">...</section>
 */

export interface RevealOptions {
  y?: number;
  opacity?: number;
  duration?: number;
  delay?: number;
  stagger?: number;
  threshold?: number;
  start?: string;
  easing?: string;
}

/** GSAP "power3.out" equivalent */
const POWER3_OUT = "cubic-bezier(0.215, 0.61, 0.355, 1)";
const DEFAULTS: Required<Omit<RevealOptions, "start" | "easing">> & {
  start: string;
  easing: string;
} = {
  y: 30,
  opacity: 0,
  duration: 0.6,
  delay: 0,
  stagger: 0,
  threshold: 0,
  start: "top 85%",
  easing: POWER3_OUT,
};

/** Convert a GSAP-style "top 85%" start string into an IntersectionObserver rootMargin. */
function startToRootMargin(start: string): string {
  const match = start.match(/top\s+(\d+(?:\.\d+)?)%/);
  if (match) {
    const pct = parseFloat(match[1]);
    const bottomInset = Math.max(0, 100 - pct);
    return `0px 0px -${bottomInset}% 0px`;
  }
  return "0px 0px -15% 0px";
}

export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function initScrollReveal(root: ParentNode = document): void {
  if (typeof window === "undefined") return;

  const containers = Array.from(
    root.querySelectorAll<HTMLElement>("[data-reveal], [data-scroll-reveal]"),
  );
  if (containers.length === 0) return;

  const reduced = prefersReducedMotion();

  for (const el of containers) {
    const y = parseFloat(el.dataset.revealY ?? String(DEFAULTS.y));
    const duration = parseFloat(
      el.dataset.revealDuration ?? String(DEFAULTS.duration),
    );
    const stagger = parseFloat(
      el.dataset.revealStagger ?? el.dataset.scrollRevealStagger ?? String(DEFAULTS.stagger),
    );
    const baseDelay = parseFloat(
      el.dataset.revealDelay ?? String(DEFAULTS.delay),
    );
    const threshold = parseFloat(
      el.dataset.revealThreshold ?? String(DEFAULTS.threshold),
    );
    const start = el.dataset.revealStart ?? DEFAULTS.start;
    const easing = el.dataset.revealEasing ?? DEFAULTS.easing;

    const targets: HTMLElement[] =
      stagger > 0
        ? (Array.from(el.children) as HTMLElement[])
        : [el];

    // Reduced motion: reveal immediately, no transition.
    if (reduced) {
      for (const t of targets) {
        t.style.opacity = "1";
        t.style.transform = "translateY(0)";
        t.style.transition = "none";
      }
      continue;
    }

    for (const t of targets) {
      const i = targets.indexOf(t);
      t.style.opacity = String(DEFAULTS.opacity);
      t.style.transform = `translateY(${y}px)`;
      t.style.willChange = "opacity, transform";
      t.style.transition = `opacity ${duration}s ${easing}, transform ${duration}s ${easing}`;
      t.style.transitionDelay = `${baseDelay + (stagger > 0 ? i * stagger : 0)}s`;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          for (const t of targets) {
            t.style.opacity = "1";
            t.style.transform = "translateY(0)";
          }
          observer.unobserve(entry.target);
        }
      },
      {
        threshold: Math.max(0, Math.min(1, threshold)),
        rootMargin: startToRootMargin(start),
      },
    );

    observer.observe(el);
  }
}

/**
 * PageTransition — Astro-native route/entrance transition.
 * Replaces the source framer-motion `PageTransition`:
 *   initial { opacity:0, y:8 } -> animate { opacity:1, y:0 }, 0.3s easeOut
 * On a static Astro MPA each navigation is a full document load, so the
 * closest equivalent is a mount-time entrance animation on the wrapped
 * content. Honors prefers-reduced-motion.
 */
export function initPageTransition(root: ParentNode = document): void {
  if (typeof window === "undefined") return;

  const els = Array.from(
    root.querySelectorAll<HTMLElement>("[data-page-transition]"),
  );
  if (els.length === 0) return;

  if (prefersReducedMotion()) {
    for (const el of els) {
      el.style.opacity = "1";
      el.style.transform = "translateY(0)";
      el.style.transition = "none";
    }
    return;
  }

  for (const el of els) {
    el.style.opacity = "0";
    el.style.transform = "translateY(8px)";
    el.style.transition = "opacity 0.3s ease-out, transform 0.3s ease-out";
    requestAnimationFrame(() => {
      el.style.opacity = "1";
      el.style.transform = "translateY(0)";
    });
  }
}

/**
 * HeroAnimator — entrance animation sequencing for hero sections.
 * Replaces the source `HeroAnimator` (GSAP timeline):
 *   - image: scale 1.05 -> 1 over 3s power2.out
 *   - lines: y 30 -> 0, opacity 0 -> 1, 0.6s, stagger 0.15, start 0.2s
 *   - ctas:  scale 0.9 -> 1, opacity 0 -> 1, 0.4s, stagger 0.1, start 0.8s
 * Honors prefers-reduced-motion (no animation).
 */
export function initHeroAnimator(root: ParentNode = document): void {
  if (typeof window === "undefined") return;
  if (prefersReducedMotion()) return;

  const container = root.querySelector<HTMLElement>("[data-hero-animator]");
  if (!container) return;

  const image = container.querySelector<HTMLElement>("[data-hero-image]");
  const lines = container.querySelectorAll<HTMLElement>("[data-hero-line]");
  const ctas = container.querySelectorAll<HTMLElement>("[data-hero-cta]");

  if (image) {
    image.style.transform = "scale(1.05)";
    image.style.transition = "transform 3s cubic-bezier(0.25, 0.46, 0.45, 0.94)";
    requestAnimationFrame(() => {
      image.style.transform = "scale(1)";
    });
  }

  lines.forEach((line, i) => {
    line.style.opacity = "0";
    line.style.transform = "translateY(30px)";
    line.style.transition =
      "opacity 0.6s cubic-bezier(0.215,0.61,0.355,1), transform 0.6s cubic-bezier(0.215,0.61,0.355,1)";
    line.style.transitionDelay = `${0.2 + i * 0.15}s`;
    requestAnimationFrame(() => {
      line.style.opacity = "1";
      line.style.transform = "translateY(0)";
    });
  });

  ctas.forEach((cta, i) => {
    cta.style.opacity = "0";
    cta.style.transform = "scale(0.9)";
    cta.style.transition =
      "opacity 0.4s cubic-bezier(0.215,0.61,0.355,1), transform 0.4s cubic-bezier(0.215,0.61,0.355,1)";
    cta.style.transitionDelay = `${0.8 + i * 0.1}s`;
    requestAnimationFrame(() => {
      cta.style.opacity = "1";
      cta.style.transform = "scale(1)";
    });
  });
}