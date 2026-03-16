(() => {
  const state = {
    isAuthenticated: false,
    userEmail: localStorage.getItem("userEmail") || "",
    isAdmin: localStorage.getItem("isAdmin") === "true",
  };

  const dom = {
    authNav: null,
    userNav: null,
    userEmailDisplay: null,
    authModal: null,
    closeAuthBtn: null,
    authForm: null,
    emailInput: null,
    passwordInput: null,
    confirmPasswordInput: null,
    confirmPasswordGroup: null,
    authTitle: null,
    authSubmitBtn: null,
    authError: null,
    authSuccess: null,
    resendVerificationWrap: null,
    resendVerificationBtn: null,
    modalSwitchToRegister: null,
    modalSwitchToLogin: null,
    showLoginBtn: null,
    showRegisterBtn: null,
    logoutBtn: null,
    mobileMenuBtn: null,
    mobileMenuPanel: null,
    mobileAuthNav: null,
    mobileUserNav: null,
    mobileShowLoginBtn: null,
    mobileShowRegisterBtn: null,
    mobileLogoutBtn: null,
    mobileUserEmailDisplay: null,
    mobileNavAdminLink: null,
  };

  let isLoginMode = true;

  function evaluatePasswordRules(password) {
    return {
      length: password.length >= 12,
      upper: /[A-Z]/.test(password),
      lower: /[a-z]/.test(password),
      digit: /\d/.test(password),
      special: /[^A-Za-z0-9]/.test(password),
    };
  }

  function countSatisfiedRules(rules) {
    return Object.values(rules).filter(Boolean).length;
  }

  function setButtonEnabled(button, enabled) {
    if (!button) return;
    button.disabled = !enabled;
    button.classList.toggle("opacity-60", !enabled);
    button.classList.toggle("cursor-not-allowed", !enabled);
  }

  function strengthLabel(score) {
    if (score <= 1) return { text: "Très faible", color: "bg-red-500" };
    if (score === 2) return { text: "Faible", color: "bg-orange-500" };
    if (score === 3) return { text: "Moyen", color: "bg-yellow-500" };
    if (score === 4) return { text: "Bon", color: "bg-blue-500" };
    return { text: "Excellent", color: "bg-green-500" };
  }

  function setRuleState(elementId, ok) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.classList.toggle("text-green-700", ok);
    el.classList.toggle("font-semibold", ok);
    el.classList.toggle("text-gray-600", !ok);
  }

  function renderStrength(prefix, password) {
    const rules = evaluatePasswordRules(password || "");
    const score = countSatisfiedRules(rules);
    const ratio = (score / 5) * 100;
    const { text, color } = strengthLabel(score);

    const bar = document.getElementById(`${prefix}StrengthBar`);
    const textNode = document.getElementById(`${prefix}StrengthText`);
    if (bar) {
      bar.style.width = `${ratio}%`;
      bar.classList.remove("bg-red-500", "bg-orange-500", "bg-yellow-500", "bg-blue-500", "bg-green-500");
      bar.classList.add(color);
    }
    if (textNode) {
      textNode.textContent = text;
      textNode.classList.remove("text-gray-500", "text-red-600", "text-orange-600", "text-yellow-700", "text-blue-700", "text-green-700");
      if (score <= 1) textNode.classList.add("text-red-600");
      else if (score === 2) textNode.classList.add("text-orange-600");
      else if (score === 3) textNode.classList.add("text-yellow-700");
      else if (score === 4) textNode.classList.add("text-blue-700");
      else textNode.classList.add("text-green-700");
    }

    setRuleState(`${prefix}RuleLength`, rules.length);
    setRuleState(`${prefix}RuleUpper`, rules.upper);
    setRuleState(`${prefix}RuleLower`, rules.lower);
    setRuleState(`${prefix}RuleDigit`, rules.digit);
    setRuleState(`${prefix}RuleSpecial`, rules.special);

    if (prefix === "register") {
      setButtonEnabled(dom.authSubmitBtn, isLoginMode || score === 5);
    }
    if (prefix === "reset") {
      const resetBtn = document.getElementById("resetPasswordSubmitBtn");
      setButtonEnabled(resetBtn, score === 5);
    }
  }

  function initDomRefs() {
    dom.authNav = document.getElementById("authNav");
    dom.userNav = document.getElementById("userNav");
    dom.userEmailDisplay = document.getElementById("userEmailDisplay");
    dom.authModal = document.getElementById("authModal");
    dom.closeAuthBtn = document.getElementById("closeAuthBtn");
    dom.authForm = document.getElementById("authForm");
    dom.emailInput = document.getElementById("email");
    dom.passwordInput = document.getElementById("password");
    dom.confirmPasswordInput = document.getElementById("confirmPassword");
    dom.confirmPasswordGroup = document.getElementById("confirmPasswordGroup");
    dom.authTitle = document.getElementById("authTitle");
    dom.authSubmitBtn = document.getElementById("authSubmitBtn");
    dom.authError = document.getElementById("authError");
    dom.authSuccess = document.getElementById("authSuccess");
    dom.resendVerificationWrap = document.getElementById("resendVerificationWrap");
    dom.resendVerificationBtn = document.getElementById("resendVerificationBtn");
    dom.modalSwitchToRegister = document.getElementById("modalSwitchToRegister");
    dom.modalSwitchToLogin = document.getElementById("modalSwitchToLogin");
    dom.showLoginBtn = document.getElementById("showLoginBtn");
    dom.showRegisterBtn = document.getElementById("showRegisterBtn");
    dom.logoutBtn = document.getElementById("logoutBtn");
    dom.mobileMenuBtn = document.getElementById("mobileMenuBtn");
    dom.mobileMenuPanel = document.getElementById("mobileMenuPanel");
    dom.mobileAuthNav = document.getElementById("mobileAuthNav");
    dom.mobileUserNav = document.getElementById("mobileUserNav");
    dom.mobileShowLoginBtn = document.getElementById("mobileShowLoginBtn");
    dom.mobileShowRegisterBtn = document.getElementById("mobileShowRegisterBtn");
    dom.mobileLogoutBtn = document.getElementById("mobileLogoutBtn");
    dom.mobileUserEmailDisplay = document.getElementById("mobileUserEmailDisplay");
    dom.mobileNavAdminLink = document.getElementById("mobileNavAdminLink");
  }

  function toggleMobileMenu(force = null) {
    if (!dom.mobileMenuPanel) return;
    const shouldOpen = force === null ? dom.mobileMenuPanel.classList.contains("hidden") : Boolean(force);
    dom.mobileMenuPanel.classList.toggle("hidden", !shouldOpen);
  }

  function applyAuthModeUi() {
    if (isLoginMode) {
      if (dom.authTitle) dom.authTitle.innerText = "Connexion";
      if (dom.authSubmitBtn) dom.authSubmitBtn.innerText = "Se connecter";
      if (dom.confirmPasswordGroup) dom.confirmPasswordGroup.classList.add("hidden");
      if (dom.confirmPasswordInput) {
        dom.confirmPasswordInput.value = "";
        dom.confirmPasswordInput.required = false;
      }
      if (dom.modalSwitchToRegister) dom.modalSwitchToRegister.classList.remove("hidden");
      if (dom.modalSwitchToLogin) dom.modalSwitchToLogin.classList.add("hidden");
      const modalForgotPasswordLink = document.getElementById("modalForgotPasswordLink");
      if (modalForgotPasswordLink) modalForgotPasswordLink.classList.remove("hidden");
      setButtonEnabled(dom.authSubmitBtn, true);
      return;
    }

    if (dom.authTitle) dom.authTitle.innerText = "Inscription";
    if (dom.authSubmitBtn) dom.authSubmitBtn.innerText = "S'inscrire";
    if (dom.confirmPasswordGroup) dom.confirmPasswordGroup.classList.remove("hidden");
    if (dom.confirmPasswordInput) dom.confirmPasswordInput.required = true;
    if (dom.modalSwitchToRegister) dom.modalSwitchToRegister.classList.add("hidden");
    if (dom.modalSwitchToLogin) dom.modalSwitchToLogin.classList.remove("hidden");
    const modalForgotPasswordLink = document.getElementById("modalForgotPasswordLink");
    if (modalForgotPasswordLink) modalForgotPasswordLink.classList.add("hidden");
    renderStrength("register", dom.passwordInput ? dom.passwordInput.value : "");
  }

  function showAuthMessage(message, isError = true) {
    if (!dom.authError || !dom.authSuccess) return;

    if (isError) {
      dom.authError.textContent = message;
      dom.authError.classList.remove("hidden");
      dom.authSuccess.classList.add("hidden");
      return;
    }

    dom.authSuccess.textContent = message;
    dom.authSuccess.classList.remove("hidden");
    dom.authError.classList.add("hidden");
    if (dom.resendVerificationWrap) dom.resendVerificationWrap.classList.add("hidden");
  }

  function clearAuthMessage() {
    if (dom.authError) dom.authError.classList.add("hidden");
    if (dom.authSuccess) dom.authSuccess.classList.add("hidden");
    if (dom.resendVerificationWrap) dom.resendVerificationWrap.classList.add("hidden");
  }

  function toggleResendVerification(show) {
    if (!dom.resendVerificationWrap) return;
    dom.resendVerificationWrap.classList.toggle("hidden", !show);
  }

  function showLoginModal(prefillMessage = "") {
    if (typeof prefillMessage !== "string") {
      prefillMessage = "";
    }
    isLoginMode = true;
    applyAuthModeUi();
    if (dom.authModal) dom.authModal.classList.remove("hidden");
    clearAuthMessage();
    if (prefillMessage) showAuthMessage(prefillMessage, true);
  }

  function showRegisterModal() {
    isLoginMode = false;
    applyAuthModeUi();
    if (dom.authModal) dom.authModal.classList.remove("hidden");
    clearAuthMessage();
  }

  function hideAuthModal() {
    if (dom.authModal) dom.authModal.classList.add("hidden");
  }

  function clearLocalAuthState() {
    localStorage.removeItem("userEmail");
    localStorage.removeItem("isAdmin");
    localStorage.removeItem("conversationId");
    state.userEmail = "";
    state.isAdmin = false;
    state.isAuthenticated = false;
  }

  async function refreshAuthState() {
    try {
      const response = await fetch("/api/auth/me");
      const data = await response.json();

      if (!response.ok || !data.ok) {
        clearLocalAuthState();
        return state;
      }

      state.isAuthenticated = true;
      state.userEmail = data.email || "";
      state.isAdmin = data.is_admin === true;
      localStorage.setItem("userEmail", state.userEmail);
      localStorage.setItem("isAdmin", state.isAdmin ? "true" : "false");
      return state;
    } catch (_) {
      clearLocalAuthState();
      return state;
    }
  }

  function updateNav() {
    if (state.isAuthenticated) {
      if (dom.authNav) dom.authNav.classList.add("hidden");
      if (dom.userNav) dom.userNav.classList.remove("hidden");
      if (dom.userEmailDisplay) dom.userEmailDisplay.innerText = state.userEmail;
      if (dom.mobileAuthNav) dom.mobileAuthNav.classList.add("hidden");
      if (dom.mobileUserNav) dom.mobileUserNav.classList.remove("hidden");
      if (dom.mobileUserEmailDisplay) dom.mobileUserEmailDisplay.innerText = state.userEmail;

      const navAdminLink = document.getElementById("navAdminLink");
      if (navAdminLink) {
        navAdminLink.classList.toggle("hidden", !state.isAdmin);
      }
      if (dom.mobileNavAdminLink) {
        dom.mobileNavAdminLink.classList.toggle("hidden", !state.isAdmin);
      }

      const overlay = document.getElementById("chatAuthOverlay");
      if (overlay) overlay.classList.add("hidden");
      return;
    }

    if (dom.authNav) dom.authNav.classList.remove("hidden");
    if (dom.userNav) dom.userNav.classList.add("hidden");
    if (dom.mobileAuthNav) dom.mobileAuthNav.classList.remove("hidden");
    if (dom.mobileUserNav) dom.mobileUserNav.classList.add("hidden");
    if (dom.mobileNavAdminLink) dom.mobileNavAdminLink.classList.add("hidden");

    const overlay = document.getElementById("chatAuthOverlay");
    if (overlay) overlay.classList.remove("hidden");
  }

  function loginReasonMessage(reason) {
    const reasons = {
      auth_required: "Vous devez vous connecter pour accéder à cette page.",
      admin_required: "Accès refusé : cette section est réservée aux administrateurs.",
      session_expired: "Votre session a expiré. Veuillez vous reconnecter.",
      logged_out: "Vous avez été déconnecté.",
    };
    return reasons[reason] || "Connectez-vous pour continuer.";
  }

  function redirectToLogin(reason = "auth_required", nextPath = "/chat") {
    const params = new URLSearchParams({ reason, next: nextPath });
    window.location.href = `/login?${params.toString()}`;
  }

  async function onAuthSubmit(event) {
    event.preventDefault();

    if (!dom.emailInput || !dom.passwordInput) return;

    const endpoint = isLoginMode ? "/api/auth/login" : "/api/auth/register";
    const password = dom.passwordInput.value;
    const confirmPassword = dom.confirmPasswordInput ? dom.confirmPasswordInput.value : "";

    if (!isLoginMode) {
      if (!confirmPassword) {
        showAuthMessage("Veuillez confirmer votre mot de passe.", true);
        return;
      }
      if (password !== confirmPassword) {
        showAuthMessage("Les mots de passe ne correspondent pas.", true);
        return;
      }
    }

    const payload = {
      email: dom.emailInput.value,
      password,
    };

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (!response.ok || !data.ok) {
        const reason = data.reason || data.error;
        if (reason === "email_not_verified") {
          showAuthMessage("Votre email n'est pas encore vérifié.", true);
          toggleResendVerification(true);
        } else {
          showAuthMessage(data.message || data.error || data.reason || "Action impossible", true);
          toggleResendVerification(false);
        }
        return;
      }

      if (!isLoginMode) {
        showAuthMessage("Inscription réussie. Vérifiez votre email puis connectez-vous.", false);
        return;
      }

      await refreshAuthState();
      updateNav();
      hideAuthModal();

      const qs = new URLSearchParams(window.location.search);
      const nextPath = qs.get("next") || "/chat";
      if (window.location.pathname === "/login") {
        window.location.href = nextPath;
      }
    } catch (_) {
      showAuthMessage("Erreur réseau.", true);
    }
  }

  async function onLogout() {
    try {
      await fetch("/api/auth/logout", { method: "POST" });
    } catch (_) {
      // no-op
    }

    clearLocalAuthState();
    updateNav();
    if (window.location.pathname === "/chat" || window.location.pathname === "/admin") {
      redirectToLogin("logged_out", "/chat");
    }
  }

  function bindEvents() {
    if (dom.showLoginBtn) {
      dom.showLoginBtn.addEventListener("click", () => showLoginModal());
    }

    if (dom.mobileShowLoginBtn) {
      dom.mobileShowLoginBtn.addEventListener("click", () => {
        showLoginModal();
        toggleMobileMenu(false);
      });
    }

    const loginPageOpenBtn = document.getElementById("loginPageOpenBtn");
    if (loginPageOpenBtn) {
      loginPageOpenBtn.addEventListener("click", () => {
        showLoginModal();
      });
    }

    const loginPageRegisterBtn = document.getElementById("loginPageRegisterBtn");
    if (loginPageRegisterBtn) {
      loginPageRegisterBtn.addEventListener("click", () => {
        showRegisterModal();
      });
    }

    if (dom.showRegisterBtn) {
      dom.showRegisterBtn.addEventListener("click", showRegisterModal);
    }

    if (dom.mobileShowRegisterBtn) {
      dom.mobileShowRegisterBtn.addEventListener("click", () => {
        showRegisterModal();
        toggleMobileMenu(false);
      });
    }

    if (dom.modalSwitchToRegister) {
      dom.modalSwitchToRegister.addEventListener("click", showRegisterModal);
    }

    if (dom.modalSwitchToLogin) {
      dom.modalSwitchToLogin.addEventListener("click", () => showLoginModal());
    }

    if (dom.closeAuthBtn) {
      dom.closeAuthBtn.addEventListener("click", hideAuthModal);
    }

    if (dom.logoutBtn) {
      dom.logoutBtn.addEventListener("click", onLogout);
    }

    if (dom.mobileLogoutBtn) {
      dom.mobileLogoutBtn.addEventListener("click", onLogout);
    }

    if (dom.mobileMenuBtn) {
      dom.mobileMenuBtn.addEventListener("click", () => toggleMobileMenu());
    }

    if (dom.authForm) {
      dom.authForm.addEventListener("submit", onAuthSubmit);
    }

    if (dom.resendVerificationBtn) {
      dom.resendVerificationBtn.addEventListener("click", async () => {
        const email = (dom.emailInput && dom.emailInput.value ? dom.emailInput.value : "").trim().toLowerCase();
        if (!email) {
          showAuthMessage("Veuillez entrer votre email pour renvoyer la vérification.", true);
          return;
        }

        try {
          const response = await fetch("/api/auth/resend-verification", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email }),
          });
          const data = await response.json();
          if (!response.ok || !data.ok) {
            showAuthMessage(data.message || data.error || "Impossible de renvoyer l'email.", true);
            return;
          }
          showAuthMessage(data.message || "Un nouvel email de validation a été envoyé.", false);
        } catch (_) {
          showAuthMessage("Erreur réseau.", true);
        }
      });
    }

    if (dom.passwordInput) {
      dom.passwordInput.addEventListener("input", () => {
        if (!isLoginMode) {
          renderStrength("register", dom.passwordInput.value || "");
        }
      });
    }
  }

  function showPageMessage(errorId, successId, message, isError = true) {
    const errorBox = document.getElementById(errorId);
    const successBox = document.getElementById(successId);
    if (!errorBox || !successBox) return;

    if (isError) {
      errorBox.textContent = message;
      errorBox.classList.remove("hidden");
      successBox.classList.add("hidden");
      return;
    }

    successBox.textContent = message;
    successBox.classList.remove("hidden");
    errorBox.classList.add("hidden");
  }

  function bindForgotPasswordForm() {
    const form = document.getElementById("forgotPasswordForm");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const emailInput = document.getElementById("forgotEmail");
      if (!emailInput) return;

      const email = (emailInput.value || "").trim();
      if (!email) {
        showPageMessage("forgotPasswordError", "forgotPasswordSuccess", "Veuillez entrer votre email.", true);
        return;
      }

      try {
        const response = await fetch("/api/auth/forgot-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        });
        const data = await response.json();

        if (!response.ok || !data.ok) {
          showPageMessage(
            "forgotPasswordError",
            "forgotPasswordSuccess",
            data.error || data.message || "Impossible d'envoyer le lien.",
            true,
          );
          return;
        }

        showPageMessage(
          "forgotPasswordError",
          "forgotPasswordSuccess",
          data.message || "Si un compte existe pour cet email, un lien a été envoyé.",
          false,
        );
      } catch (_) {
        showPageMessage("forgotPasswordError", "forgotPasswordSuccess", "Erreur réseau.", true);
      }
    });
  }

  function bindResetPasswordForm() {
    const form = document.getElementById("resetPasswordForm");
    if (!form) return;

    const newPasswordInput = document.getElementById("newPassword");
    if (newPasswordInput) {
      newPasswordInput.addEventListener("input", () => {
        renderStrength("reset", newPasswordInput.value || "");
      });
      renderStrength("reset", newPasswordInput.value || "");
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const tokenInput = document.getElementById("resetToken");
      const newPasswordInput = document.getElementById("newPassword");
      const confirmInput = document.getElementById("confirmNewPassword");
      if (!tokenInput || !newPasswordInput || !confirmInput) return;

      const token = (tokenInput.value || "").trim();
      const password = newPasswordInput.value || "";
      const confirm = confirmInput.value || "";

      if (!token) {
        showPageMessage("resetPasswordError", "resetPasswordSuccess", "Lien invalide : token manquant.", true);
        return;
      }

      if (!password || !confirm) {
        showPageMessage("resetPasswordError", "resetPasswordSuccess", "Veuillez remplir tous les champs.", true);
        return;
      }

      if (password !== confirm) {
        showPageMessage("resetPasswordError", "resetPasswordSuccess", "Les mots de passe ne correspondent pas.", true);
        return;
      }

      try {
        const response = await fetch("/api/auth/reset-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token, password }),
        });
        const data = await response.json();

        if (!response.ok || !data.ok) {
          showPageMessage(
            "resetPasswordError",
            "resetPasswordSuccess",
            data.error || data.message || "Réinitialisation impossible.",
            true,
          );
          return;
        }

        showPageMessage(
          "resetPasswordError",
          "resetPasswordSuccess",
          data.message || "Mot de passe mis à jour. Vous pouvez vous connecter.",
          false,
        );
        form.reset();
      } catch (_) {
        showPageMessage("resetPasswordError", "resetPasswordSuccess", "Erreur réseau.", true);
      }
    });
  }

  async function boot() {
    initDomRefs();
    applyAuthModeUi();
    bindEvents();
    bindForgotPasswordForm();
    bindResetPasswordForm();
    renderStrength("register", dom.passwordInput ? dom.passwordInput.value : "");

    await refreshAuthState();
    updateNav();

    if (window.location.pathname === "/login") {
      const ctx = window.__JR_LOGIN_CONTEXT__ || {};
      if (!state.isAuthenticated) {
        // On laisse la page afficher uniquement la carte explicative.
      } else {
        const nextPath = ctx.next || "/chat";
        window.location.href = nextPath;
      }
    }

    window.dispatchEvent(new CustomEvent("jr:auth-ready", { detail: { ...state } }));
  }

  window.JRAuth = {
    getState: () => ({ ...state }),
    refreshAuthState,
    updateNav,
    clearLocalAuthState,
    redirectToLogin,
  };

  document.addEventListener("DOMContentLoaded", boot);
})();
