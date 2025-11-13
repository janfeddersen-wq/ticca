"""Shared HTML templates for OAuth flow with clean, professional Ticca Bar styling."""

from __future__ import annotations

from typing import Optional, Tuple


def oauth_success_html(service_name: str, extra_message: Optional[str] = None) -> str:
    """Return a clean, professional OAuth success page with Ticca Bar vibes."""
    clean_service = service_name.strip() or "OAuth"
    detail = f"<p class='detail'>{extra_message}</p>" if extra_message else ""

    return (
        "<!DOCTYPE html>"
        "<html lang='en'><head><meta charset='utf-8'>"
        "<title>Authentication Successful</title>"
        "<style>"
        "html,body{margin:0;padding:0;height:100%;overflow:hidden;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0e1a;color:#e5e7eb;}"
        "body{display:flex;align-items:center;justify-content:center;}"
        ".container{position:relative;width:90%;max-width:600px;padding:48px;background:rgba(15,23,42,0.85);border-radius:16px;backdrop-filter:blur(12px);box-shadow:0 20px 60px rgba(0,0,0,0.5);text-align:center;border:1px solid rgba(148,163,184,0.15);}"
        "h1{font-size:2em;margin:0 0 12px;color:#f1f5f9;font-weight:600;letter-spacing:-0.02em;}"
        "p{font-size:1.05em;margin:12px 0;color:#94a3b8;line-height:1.6;}"
        ".detail{font-size:0.95em;opacity:0.8;}"
        ".status-icon{font-size:3.5em;margin-bottom:16px;animation:checkPulse 2s ease-in-out infinite;}"
        "@keyframes checkPulse{0%,100%{transform:scale(1);opacity:1;}50%{transform:scale(1.05);opacity:0.9;}}"
        ".progress-container{width:100%;height:4px;background:rgba(148,163,184,0.2);border-radius:2px;margin:24px 0;overflow:hidden;}"
        ".progress-bar{height:100%;background:linear-gradient(90deg,#3b82f6,#8b5cf6);border-radius:2px;animation:fillBar 3s ease-out forwards;}"
        "@keyframes fillBar{0%{width:0%;}100%{width:100%;}}"
        ".ticca-bars{display:flex;justify-content:center;gap:4px;margin:32px 0 24px;}"
        ".bar{width:8px;height:40px;background:linear-gradient(180deg,#3b82f6,#1e40af);border-radius:4px;animation:barPulse 1.5s ease-in-out infinite;}"
        ".bar:nth-child(1){animation-delay:0s;height:32px;}"
        ".bar:nth-child(2){animation-delay:0.1s;height:48px;}"
        ".bar:nth-child(3){animation-delay:0.2s;height:40px;}"
        ".bar:nth-child(4){animation-delay:0.3s;height:56px;}"
        ".bar:nth-child(5){animation-delay:0.4s;height:36px;}"
        "@keyframes barPulse{0%,100%{opacity:0.4;transform:scaleY(0.9);}50%{opacity:1;transform:scaleY(1.1);}}"
        ".service-badge{display:inline-block;padding:8px 16px;background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.3);border-radius:20px;color:#60a5fa;font-size:0.9em;font-weight:500;margin-bottom:24px;}"
        "</style>"
        "</head><body>"
        "<div class='container'>"
        f"<div class='service-badge'>{clean_service}</div>"
        "<div class='status-icon'>✓</div>"
        "<h1>Authentication Successful</h1>"
        "<p>Your authentication has been completed successfully.</p>"
        f"{detail}"
        "<div class='ticca-bars'>"
        "<div class='bar'></div>"
        "<div class='bar'></div>"
        "<div class='bar'></div>"
        "<div class='bar'></div>"
        "<div class='bar'></div>"
        "</div>"
        "<div class='progress-container'><div class='progress-bar'></div></div>"
        "<p class='detail'>This window will close automatically in a moment.</p>"
        "</div>"
        "<script>setTimeout(()=>window.close(),3500);</script>"
        "</body></html>"
    )


def oauth_failure_html(service_name: str, reason: str) -> str:
    """Return a clean, professional OAuth failure page with Ticca Bar vibes."""
    clean_service = service_name.strip() or "OAuth"
    clean_reason = reason.strip() or "Authentication failed"

    return (
        "<!DOCTYPE html>"
        "<html lang='en'><head><meta charset='utf-8'>"
        "<title>Authentication Failed</title>"
        "<style>"
        "html,body{margin:0;padding:0;height:100%;overflow:hidden;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0e1a;color:#e5e7eb;}"
        "body{display:flex;align-items:center;justify-content:center;}"
        ".container{position:relative;width:90%;max-width:600px;padding:48px;background:rgba(15,23,42,0.85);border-radius:16px;backdrop-filter:blur(12px);box-shadow:0 20px 60px rgba(0,0,0,0.5);text-align:center;border:1px solid rgba(148,163,184,0.15);}"
        "h1{font-size:2em;margin:0 0 12px;color:#f87171;font-weight:600;letter-spacing:-0.02em;}"
        "p{font-size:1.05em;margin:12px 0;color:#94a3b8;line-height:1.6;}"
        ".error-msg{font-size:0.95em;color:#fca5a5;background:rgba(220,38,38,0.1);border:1px solid rgba(220,38,38,0.2);padding:12px 16px;border-radius:8px;margin:20px 0;}"
        ".status-icon{font-size:3.5em;margin-bottom:16px;animation:errorPulse 2s ease-in-out infinite;color:#f87171;}"
        "@keyframes errorPulse{0%,100%{transform:scale(1);opacity:1;}50%{transform:scale(1.05);opacity:0.8;}}"
        ".ticca-bars{display:flex;justify-content:center;gap:4px;margin:32px 0 24px;}"
        ".bar{width:8px;height:40px;background:linear-gradient(180deg,#dc2626,#991b1b);border-radius:4px;animation:barFade 1.5s ease-in-out infinite;}"
        ".bar:nth-child(1){animation-delay:0s;height:32px;}"
        ".bar:nth-child(2){animation-delay:0.1s;height:48px;}"
        ".bar:nth-child(3){animation-delay:0.2s;height:40px;}"
        ".bar:nth-child(4){animation-delay:0.3s;height:56px;}"
        ".bar:nth-child(5){animation-delay:0.4s;height:36px;}"
        "@keyframes barFade{0%,100%{opacity:0.3;transform:scaleY(0.85);}50%{opacity:0.6;transform:scaleY(1);}}"
        ".service-badge{display:inline-block;padding:8px 16px;background:rgba(220,38,38,0.15);border:1px solid rgba(220,38,38,0.3);border-radius:20px;color:#fca5a5;font-size:0.9em;font-weight:500;margin-bottom:24px;}"
        ".buttons{margin-top:26px;}"
        ".buttons a{display:inline-block;margin:6px 12px;padding:12px 24px;border-radius:8px;background:rgba(59,130,246,0.15);color:#93c5fd;text-decoration:none;font-weight:500;border:1px solid rgba(59,130,246,0.3);transition:all 0.3s;}"
        ".buttons a:hover{background:rgba(59,130,246,0.25);transform:translateY(-2px);border-color:rgba(59,130,246,0.5);}"
        "</style>"
        "</head><body>"
        "<div class='container'>"
        f"<div class='service-badge'>{clean_service}</div>"
        "<div class='status-icon'>✗</div>"
        "<h1>Authentication Failed</h1>"
        "<p>We encountered an issue during the authentication process.</p>"
        f"<div class='error-msg'>{clean_reason}</div>"
        "<div class='ticca-bars'>"
        "<div class='bar'></div>"
        "<div class='bar'></div>"
        "<div class='bar'></div>"
        "<div class='bar'></div>"
        "<div class='bar'></div>"
        "</div>"
        "<p>Please try again from Ticca.</p>"
        "<div class='buttons'>"
        "<a href='https://github.com/code-puppy/ticca' target='_blank'>View Documentation</a>"
        "</div>"
        "</div>"
        "</body></html>"
    )


# Legacy constants - no longer used but kept for backwards compatibility
_SUCCESS_PUPPIES = ()
_FAILURE_PUPPIES = ()
_STRAFE_SHELLS: Tuple[Tuple[float, float], ...] = ()


def _build_artillery(projectile: str, *, shells_only: bool = False) -> str:
    """Legacy function - no longer used."""
    return ""


def _service_targets(service_name: str) -> Tuple[str, str, str, str]:
    """Legacy function - no longer used."""
    return "", "", "", ""
