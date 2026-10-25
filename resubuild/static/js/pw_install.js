
(() => {
    "use strict";

    let installPrompt = null;
    let button = document.getElementById("installAppButton");

    // Create an installation button automatically on pages that do not
    // already contain one, such as the home page.
    if (!button && document.body) {
        button = document.createElement("button");
        button.id = "installAppButton";
        button.type = "button";
        button.textContent = "↓ Install app";
        button.setAttribute(
            "aria-label",
            "Install BxB AI Resume Builder"
        );

        button.style.cssText = [
            "position:fixed",
            "right:16px",
            "bottom:16px",
            "z-index:99999",
            "border:1px solid rgba(255,255,255,.18)",
            "border-radius:12px",
            "padding:12px 16px",
            "background:linear-gradient(110deg,#c2b4ff,#9d8cff)",
            "color:#111020",
            "font:700 13px/1.2 system-ui,sans-serif",
            "box-shadow:0 8px 28px rgba(0,0,0,.25)",
            "cursor:pointer"
        ].join(";");

        document.body.appendChild(button);
    }

    function isStandalone() {
        return (
            window.matchMedia("(display-mode: standalone)").matches ||
            window.matchMedia("(display-mode: fullscreen)").matches ||
            navigator.standalone === true
        );
    }

    function setButtonState() {
        if (!button) return;

        button.hidden = isStandalone();
    }

    function manualInstallInstructions() {
        const ua = navigator.userAgent || "";

        const isIOS =
            /iPad|iPhone|iPod/.test(ua) ||
            (
                navigator.platform === "MacIntel" &&
                navigator.maxTouchPoints > 1
            );

        const isSafari =
            /Safari/i.test(ua) &&
            !/Chrome|CriOS|Edg|FxiOS|OPR/i.test(ua);

        const isMacSafari =
            /Macintosh|Mac OS X/i.test(ua) && isSafari;

        const isAndroid = /Android/i.test(ua);

        let message;

        if (isIOS) {
            message =
                "To install BxB Resume Builder on iPhone or iPad:\n\n" +
                "1. Open this website in Safari.\n" +
                "2. Tap the Share button.\n" +
                "3. Select 'Add to Home Screen'.\n" +
                "4. Tap Add.";
        } else if (isMacSafari) {
            message =
                "To install BxB Resume Builder on macOS:\n\n" +
                "Open Safari's File menu and select 'Add to Dock' " +
                "if the option is available.";
        } else if (isAndroid) {
            message =
                "To install BxB Resume Builder on Android:\n\n" +
                "Open your browser menu and choose 'Install app' " +
                "or 'Add to Home screen' if available.";
        } else {
            message =
                "To install BxB Resume Builder:\n\n" +
                "Open your browser menu and look for 'Install app'.\n\n" +
                "In Chrome or Edge on desktop, you may also see an " +
                "installation icon near the address bar.\n\n" +
                "If no install option appears, make sure the website " +
                "uses HTTPS and its PWA manifest and service worker " +
                "are configured correctly.";
        }

        window.alert(message);
    }

    // Chromium-based browsers can provide a native installation prompt.
    window.addEventListener("beforeinstallprompt", (event) => {
        event.preventDefault();

        installPrompt = event;

        if (button) {
            button.hidden = false;
            button.textContent = "↓ Install app";
        }
    });

    // Hide the install button after successful installation.
    window.addEventListener("appinstalled", () => {
        installPrompt = null;

        if (button) {
            button.hidden = true;
        }

        const status = document.getElementById("pwaInstallStatus");

        if (status) {
            status.textContent = "BxB Resume Builder installed.";
        }
    });

    if (button) {
        button.addEventListener("click", async () => {
            if (isStandalone()) {
                button.hidden = true;
                return;
            }

            if (!installPrompt) {
                manualInstallInstructions();
                return;
            }

            button.disabled = true;
            button.textContent = "Opening installer...";

            try {
                installPrompt.prompt();

                const result = await installPrompt.userChoice;

                if (result?.outcome === "accepted") {
                    button.textContent = "Installing...";
                } else {
                    button.textContent = "↓ Install app";
                }
            } catch (error) {
                console.error(
                    "BxB PWA installation prompt failed:",
                    error
                );

                manualInstallInstructions();
                button.textContent = "↓ Install app";
            } finally {
                installPrompt = null;
                button.disabled = false;
            }
        });
    }

    setButtonState();

    const standaloneQuery =
        window.matchMedia("(display-mode: standalone)");

    if (typeof standaloneQuery.addEventListener === "function") {
        standaloneQuery.addEventListener("change", setButtonState);
    } else if (typeof standaloneQuery.addListener === "function") {
        standaloneQuery.addListener(setButtonState);
    }

    // Service workers require HTTPS, except on localhost during development.
    const isSecureContext =
        window.isSecureContext ||
        location.hostname === "localhost" ||
        location.hostname === "127.0.0.1";

    if ("serviceWorker" in navigator && isSecureContext) {
        window.addEventListener("load", () => {
            navigator.serviceWorker
                .register("/service-worker.js", { scope: "/" })
                .then((registration) => {
                    console.info(
                        "BxB PWA service worker ready:",
                        registration.scope
                    );
                })
                .catch((error) => {
                    console.error(
                        "BxB PWA service worker registration failed:",
                        error
                    );
                });
        });
    }
})();
